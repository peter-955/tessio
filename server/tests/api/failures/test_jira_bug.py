from datetime import UTC, datetime, timedelta

import pytest
from httpx import AsyncClient
from sqlalchemy import update

from app.container import Container
from app.modules.failures import FailureEventKind, FailureStatus
from app.modules.failures.infrastructure import FailureTable
from app.modules.jira import JiraDocumentBlockKind, JiraIssueRejectedError, JiraPermission, JiraUnreachableError
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from app.shared.typing.enums import JobName, QueueName
from tests.api.failures.failure_steps import list_event_rows, seed_scenario
from tests.api.failures.jira_bug_steps import (
    ACTUAL_RESULT,
    STEP_ERROR,
    find_failure_row,
    get_fake_jira_client,
    make_failing_result_data_driven,
    mark_story_written_in_tessio,
    preview_jira_issue,
    request_jira_issue,
    run_create_issue_job,
    seed_jira_bug_scenario,
    set_bug_issue_type,
    set_connection_create_access,
    unlink_project_from_jira,
)
from tests.conftest import RecordingMailer
from tests.support.recording_job_queue import RecordingJobQueue
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher

PNG_BYTES = b"\x89PNG screenshot"


@pytest.mark.parametrize("role", [ProjectRole.QC, ProjectRole.DEV, ProjectRole.ADMIN])
async def test_creating_a_jira_bug_queues_the_job_and_marks_the_failure_pending(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
    recording_live_event_publisher: RecordingLiveEventPublisher,
    role: ProjectRole,
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer, role)
    recording_job_queue.jobs.clear()
    recording_live_event_publisher.events.clear()

    response = await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)

    assert response.status_code == 202, response.text
    body = response.json()
    assert body["isJiraIssuePending"] is True
    assert body["jiraIssueKey"] is None
    assert body["jiraIssueErrorCode"] is None
    assert [(job.queue_name, job.job_name, job.data, job.job_id) for job in recording_job_queue.jobs] == [
        (
            QueueName.JIRA,
            JobName.JIRA_CREATE_ISSUE,
            {
                "projectId": str(bug.scenario.project.id),
                "failureId": str(bug.failure_id),
                "requestedBy": str(bug.scenario.runner.user_id),
            },
            f"jira-create-issue:{bug.failure_id}",
        )
    ]
    assert [event.type for event in recording_live_event_publisher.events] == [LiveEventType.FAILURE_CHANGED]


async def test_a_second_request_while_pending_or_linked_is_refused(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    assert (await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)).status_code == 202
    recording_job_queue.jobs.clear()

    pending = await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)
    await run_create_issue_job(container, bug, bug.scenario.runner.user_id)
    linked = await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)

    assert pending.status_code == 409
    assert pending.json()["code"] == "JIRA_ISSUE_ALREADY_LINKED"
    assert linked.status_code == 409
    assert linked.json()["code"] == "JIRA_ISSUE_ALREADY_LINKED"
    assert recording_job_queue.jobs == []


async def test_a_stale_pending_request_can_be_sent_again(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    assert (await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)).status_code == 202
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(FailureTable)
            .where(FailureTable.id == bug.failure_id)
            .values(jira_issue_requested_at=datetime.now(UTC) - timedelta(hours=1))
        )

    response = await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)

    assert response.status_code == 202


async def test_a_project_without_jira_is_refused(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    await unlink_project_from_jira(container, bug.scenario.project.id)
    recording_job_queue.jobs.clear()

    created = await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)
    preview = await preview_jira_issue(client, bug.scenario.project.key, bug.failure_id)

    assert created.status_code == 409
    assert created.json()["code"] == "JIRA_NOT_CONFIGURED"
    assert preview.status_code == 409
    assert preview.json()["code"] == "JIRA_NOT_CONFIGURED"
    assert recording_job_queue.jobs == []


async def test_an_account_that_cannot_create_issues_is_refused_before_queueing(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    await set_connection_create_access(container, False)
    recording_job_queue.jobs.clear()

    response = await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)

    assert response.status_code == 409
    assert response.json()["code"] == "JIRA_WRITE_NOT_ALLOWED"
    assert recording_job_queue.jobs == []


async def test_a_viewer_and_a_ba_cannot_create_a_jira_bug(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    for role in (ProjectRole.VIEWER, ProjectRole.BA, ProjectRole.PM):
        bug = await seed_jira_bug_scenario(client, container, recording_mailer, role)

        response = await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)

        assert response.status_code == 403, role
        assert response.json()["code"] == "PERMISSION_DENIED"


async def test_the_preview_shows_the_summary_and_description_the_job_will_send(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    await set_bug_issue_type(container, bug.scenario.project.id, "Defect")

    response = await preview_jira_issue(client, bug.scenario.project.key, bug.failure_id)

    assert response.status_code == 200, response.text
    body = response.json()
    project = bug.scenario.project
    assert body["jiraProjectKey"] == project.key
    assert body["issueTypeName"] == "Defect"
    assert body["summary"] == "TC-1 Case 1: step 2 failed"
    assert body["linkedStoryJiraKey"] == bug.scenario.story.jira_key
    assert body["hasScreenshot"] is True
    description = body["description"]
    assert f"while testing {bug.scenario.story.jira_key}" in description
    assert "Preconditions\n\nA signed-in shopper with one item in the cart" in description
    assert "Steps to reproduce\n\n1. Open the cart\n2. Pay by card\n\n" in description
    assert "Open the receipt" not in description
    assert "Expected result\n\nThe payment is accepted" in description
    assert f"Actual result (step 2)\n\n{ACTUAL_RESULT}\n\n{STEP_ERROR}" in description
    assert "Environment\n\nStaging " in description
    assert "(https://staging.tessio.test)" in description
    assert f"/projects/{project.key}/failures/{bug.failure_id}" in description


async def test_the_preview_of_a_data_driven_failure_fills_in_the_failing_row(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    await make_failing_result_data_driven(container, bug, iteration=1)

    response = await preview_jira_issue(client, bug.scenario.project.key, bug.failure_id)

    assert response.status_code == 200, response.text
    description = response.json()["description"]
    assert "Test data (iteration 2)\n\n- card = 4000 0000 0000 0002\n- outcome = declined" in description
    assert "Preconditions\n\nA shopper paying with 4000 0000 0000 0002" in description
    assert "Steps to reproduce\n\n1. Open the cart\n2. Pay with card 4000 0000 0000 0002\n\n" in description
    assert "Expected result\n\nThe payment is declined" in description
    assert "{{" not in description
    assert "4242" not in description


async def test_the_job_creates_the_issue_attaches_the_screenshot_and_links_the_story(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    assert (await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)).status_code == 202
    read_keys: list[str] = []

    async def read_object(key: str) -> bytes | None:
        read_keys.append(key)
        return PNG_BYTES

    monkeypatch.setattr(container.object_storage, "read_object", read_object)
    fake_jira = get_fake_jira_client(container)
    recording_live_event_publisher.events.clear()

    await run_create_issue_job(container, bug, bug.scenario.runner.user_id)

    project_key = bug.scenario.project.key
    assert len(fake_jira.created_issues) == 1
    created = fake_jira.created_issues[0]
    assert created.jira_project_key == project_key
    assert created.issue_type_name == "Bug"
    assert created.summary == "TC-1 Case 1: step 2 failed"
    assert any(block.kind is JiraDocumentBlockKind.ORDERED_LIST for block in created.description)
    issue_key = f"{project_key}-101"
    assert [(item.issue_key, item.attachment.file_name, item.attachment.content) for item in fake_jira.attachments] == [
        (issue_key, "step.png", PNG_BYTES)
    ]
    assert len(read_keys) == 1
    assert [(link.inward_issue_key, link.outward_issue_key) for link in fake_jira.links] == [
        (issue_key, bug.scenario.story.jira_key)
    ]
    row = await find_failure_row(container, bug.failure_id)
    assert row.jira_issue_key == issue_key
    assert row.jira_issue_url == f"https://team.atlassian.net/browse/{issue_key}"
    assert row.jira_issue_status == "To Do"
    assert row.jira_issue_done_at is None
    assert row.jira_issue_requested_at is None
    assert row.jira_issue_error_code is None
    assert row.status == FailureStatus.OPEN
    events = await list_event_rows(container, bug.failure_id)
    assert [(event.kind, event.jira_issue_key, event.actor_id) for event in events][-1] == (
        FailureEventKind.JIRA_ISSUE_CREATED,
        issue_key,
        bug.scenario.runner.user_id,
    )
    assert [event.type for event in recording_live_event_publisher.events] == [LiveEventType.FAILURE_CHANGED]
    detail = await client.get(f"/api/projects/{project_key}/failures/{bug.failure_id}")
    assert detail.json()["jiraIssueKey"] == issue_key
    assert detail.json()["isJiraIssuePending"] is False
    assert detail.json()["events"][-1]["kind"] == "jira_issue_created"
    assert detail.json()["events"][-1]["jiraIssueKey"] == issue_key


async def test_running_the_job_twice_creates_one_issue(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)

    await run_create_issue_job(container, bug)
    await run_create_issue_job(container, bug)

    assert len(get_fake_jira_client(container).created_issues) == 1


async def test_a_story_written_in_tessio_is_not_linked(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    await mark_story_written_in_tessio(container, bug.scenario.story.id)

    await run_create_issue_job(container, bug)

    fake_jira = get_fake_jira_client(container)
    assert len(fake_jira.created_issues) == 1
    assert fake_jira.links == []


async def test_a_jira_403_records_write_not_allowed_on_the_failure(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    assert (await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)).status_code == 202
    fake_jira = get_fake_jira_client(container)
    fake_jira.missing_permissions_by_project_key[bug.scenario.project.key] = frozenset({JiraPermission.CREATE_ISSUES})
    recording_live_event_publisher.events.clear()

    await run_create_issue_job(container, bug, bug.scenario.runner.user_id)

    row = await find_failure_row(container, bug.failure_id)
    assert row.jira_issue_key is None
    assert row.jira_issue_error_code == "JIRA_WRITE_NOT_ALLOWED"
    assert row.jira_issue_requested_at is None
    events = await list_event_rows(container, bug.failure_id)
    assert (events[-1].kind, events[-1].error_code) == (FailureEventKind.JIRA_ISSUE_FAILED, "JIRA_WRITE_NOT_ALLOWED")
    assert [event.type for event in recording_live_event_publisher.events] == [LiveEventType.FAILURE_CHANGED]
    detail = await client.get(f"/api/projects/{bug.scenario.project.key}/failures/{bug.failure_id}")
    assert detail.json()["jiraIssueErrorCode"] == "JIRA_WRITE_NOT_ALLOWED"
    assert detail.json()["isJiraIssuePending"] is False


async def test_a_refused_issue_type_is_recorded_and_can_be_retried(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    assert (await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)).status_code == 202
    get_fake_jira_client(container).write_errors.append(JiraIssueRejectedError())

    await run_create_issue_job(container, bug)
    refused_row = await find_failure_row(container, bug.failure_id)
    retried = await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)

    assert refused_row.jira_issue_error_code == "INVALID_REQUEST"
    assert refused_row.jira_issue_requested_at is None
    assert retried.status_code == 202
    assert (await find_failure_row(container, bug.failure_id)).jira_issue_error_code is None


async def test_an_unreachable_jira_keeps_the_request_pending_and_lets_the_job_retry(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    assert (await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)).status_code == 202
    fake_jira = get_fake_jira_client(container)
    fake_jira.write_errors.append(JiraUnreachableError())

    with pytest.raises(JiraUnreachableError):
        await run_create_issue_job(container, bug)
    pending_row = await find_failure_row(container, bug.failure_id)
    await run_create_issue_job(container, bug)

    assert pending_row.jira_issue_error_code == "JIRA_UNREACHABLE"
    assert pending_row.jira_issue_requested_at is not None
    row = await find_failure_row(container, bug.failure_id)
    assert row.jira_issue_key is not None
    assert row.jira_issue_error_code is None
    assert len(fake_jira.created_issues) == 1
    kinds = [event.kind for event in await list_event_rows(container, bug.failure_id)]
    assert FailureEventKind.JIRA_ISSUE_FAILED not in kinds
    assert kinds.count(FailureEventKind.JIRA_ISSUE_CREATED) == 1


async def test_the_job_records_a_project_unlinked_after_the_request(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    assert (await request_jira_issue(client, bug.scenario.project.key, bug.failure_id)).status_code == 202
    await unlink_project_from_jira(container, bug.scenario.project.id)

    await run_create_issue_job(container, bug)

    row = await find_failure_row(container, bug.failure_id)
    assert row.jira_issue_error_code == "JIRA_NOT_CONFIGURED"
    assert get_fake_jira_client(container).created_issues == []


async def test_the_job_masks_secrets_in_the_bug(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, monkeypatch: pytest.MonkeyPatch
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)

    async def list_secret_values(project_id: object, environment_id: object) -> list[str]:
        return ["Declined"]

    monkeypatch.setattr(container.secret_value_reader, "list_secret_values", list_secret_values)

    await run_create_issue_job(container, bug)

    created = get_fake_jira_client(container).created_issues[0]
    texts = [text for block in created.description for text in block.texts]
    assert all("Declined" not in text for text in texts)
    assert any("The card form shows '" in text for text in texts)


async def test_another_projects_failure_cannot_get_a_jira_bug(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_job_queue: RecordingJobQueue,
) -> None:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    other = await seed_scenario(client, container, recording_mailer)
    recording_job_queue.jobs.clear()

    created = await request_jira_issue(client, other.project.key, bug.failure_id)
    previewed = await preview_jira_issue(client, other.project.key, bug.failure_id)

    assert created.status_code == 404, created.text
    assert created.json()["code"] == "NOT_FOUND"
    assert previewed.status_code == 404, previewed.text
    assert previewed.json()["code"] == "NOT_FOUND"
    assert recording_job_queue.jobs == []
    assert (await find_failure_row(container, bug.failure_id)).jira_issue_requested_at is None

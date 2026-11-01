from datetime import UTC, datetime

import pytest
from httpx import AsyncClient, Response

from app.modules.stories import ActiveFailureCounter, RunningRunChecker, StoryNotFoundError
from app.modules.stories import TestStatus as StoryTestStatus
from app.modules.stories.infrastructure import StaticActiveFailureCounter, StaticRunningRunChecker
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.stories.conftest import StoriesTestContainer
from tests.api.stories.story_steps import (
    build_issue,
    build_sprint,
    find_story_row,
    run_sync,
    seed_jira_connection,
    set_board,
    set_test_status,
)
from tests.api.test_data.project_steps import SeededProject, archive_project, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.fakes.fake_jira_client import FakeJiraClient
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def seed_story(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> tuple[SeededProject, str]:
    project = await seed_project(stories_container)
    admin_id = await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.ADMIN)
    await seed_jira_connection(stories_container, admin_id)
    set_board(fake_jira_client, project, {build_sprint(1): [build_issue(project.key, 1, criteria=["Pay"])]})
    await run_sync(stories_container, project.id)
    return project, f"{project.key}-1"


async def put_test_status(client: AsyncClient, project: SeededProject, jira_key: str, test_status: str) -> Response:
    return await client.put(
        f"/api/projects/{project.key}/stories/{jira_key}/test-status", json={"testStatus": test_status}
    )


@pytest.mark.parametrize("role", [ProjectRole.DEV, ProjectRole.ADMIN])
async def test_dev_and_admin_mark_a_story_ready_and_back(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
    role: ProjectRole,
) -> None:
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    user_id = await sign_up_member(client, stories_container, recording_mailer, project, role)

    ready = await put_test_status(client, project, jira_key, "ready_for_test")

    assert ready.status_code == 200
    assert ready.json()["testStatus"] == "ready_for_test"
    assert ready.json()["availableTestStatuses"] == ["not_started"]
    assert ready.json()["testStatusChangedAt"] is not None
    row = await find_story_row(stories_container, project, jira_key)
    assert row is not None
    assert row.test_status_changed_by == user_id
    back = await put_test_status(client, project, jira_key, "not_started")
    assert back.status_code == 200
    assert back.json()["testStatus"] == "not_started"


@pytest.mark.parametrize("role", [ProjectRole.QC, ProjectRole.ADMIN])
async def test_qc_and_admin_sign_off_from_in_test_and_switch_between_passed_and_failed(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
    role: ProjectRole,
) -> None:
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    await set_test_status(stories_container, project, jira_key, StoryTestStatus.IN_TEST)
    await sign_up_member(client, stories_container, recording_mailer, project, role)

    passed = await put_test_status(client, project, jira_key, "passed")
    failed = await put_test_status(client, project, jira_key, "failed")
    passed_again = await put_test_status(client, project, jira_key, "passed")

    assert [passed.status_code, failed.status_code, passed_again.status_code] == [200, 200, 200]
    assert passed_again.json()["testStatus"] == "passed"
    assert passed_again.json()["availableTestStatuses"] == ["failed"]


async def test_dev_hands_a_failed_story_back_to_ready_for_test(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    await set_test_status(stories_container, project, jira_key, StoryTestStatus.FAILED)
    await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.DEV)

    response = await put_test_status(client, project, jira_key, "ready_for_test")

    assert response.status_code == 200
    assert response.json()["testStatus"] == "ready_for_test"


@pytest.mark.parametrize(
    ("current", "target"),
    [
        (StoryTestStatus.NOT_STARTED, "in_test"),
        (StoryTestStatus.READY_FOR_TEST, "in_test"),
        (StoryTestStatus.NOT_STARTED, "passed"),
        (StoryTestStatus.READY_FOR_TEST, "failed"),
        (StoryTestStatus.PASSED, "not_started"),
        (StoryTestStatus.IN_TEST, "ready_for_test"),
    ],
)
async def test_disallowed_transitions_are_refused(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
    current: StoryTestStatus,
    target: str,
) -> None:
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    await set_test_status(stories_container, project, jira_key, current)

    response = await put_test_status(client, project, jira_key, target)

    assert response.status_code == 409
    assert response.json()["code"] == "INVALID_STATUS_TRANSITION"


async def test_the_same_status_is_a_no_op_without_an_event(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    recording_live_event_publisher.events.clear()

    response = await put_test_status(client, project, jira_key, "not_started")

    assert response.status_code == 200
    assert response.json()["testStatusChangedAt"] is None
    assert recording_live_event_publisher.events == []


@pytest.mark.parametrize(
    ("role", "current", "target"),
    [
        (ProjectRole.PM, StoryTestStatus.NOT_STARTED, "ready_for_test"),
        (ProjectRole.PM, StoryTestStatus.IN_TEST, "passed"),
        (ProjectRole.QC, StoryTestStatus.NOT_STARTED, "ready_for_test"),
        (ProjectRole.DEV, StoryTestStatus.IN_TEST, "passed"),
        (ProjectRole.VIEWER, StoryTestStatus.IN_TEST, "failed"),
    ],
)
async def test_roles_without_the_capability_are_forbidden(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
    role: ProjectRole,
    current: StoryTestStatus,
    target: str,
) -> None:
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    await set_test_status(stories_container, project, jira_key, current)
    await sign_up_member(client, stories_container, recording_mailer, project, role)

    response = await put_test_status(client, project, jira_key, target)

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


async def test_active_failures_block_passed_but_not_failed(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    counter: ActiveFailureCounter = StaticActiveFailureCounter(1)
    stories_container.__dict__["active_failure_counter"] = counter
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    await set_test_status(stories_container, project, jira_key, StoryTestStatus.IN_TEST)

    blocked = await put_test_status(client, project, jira_key, "passed")
    failed = await put_test_status(client, project, jira_key, "failed")

    assert blocked.status_code == 409
    assert blocked.json()["code"] == "STORY_SIGN_OFF_BLOCKED"
    assert failed.status_code == 200
    assert failed.json()["testStatus"] == "failed"


async def test_a_running_run_blocks_passed_but_not_failed(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    checker: RunningRunChecker = StaticRunningRunChecker(True)
    stories_container.__dict__["running_run_checker"] = checker
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    await set_test_status(stories_container, project, jira_key, StoryTestStatus.FAILED)

    blocked = await put_test_status(client, project, jira_key, "passed")
    ready = await put_test_status(client, project, jira_key, "ready_for_test")

    assert blocked.status_code == 409
    assert blocked.json()["code"] == "STORY_SIGN_OFF_BLOCKED"
    assert ready.status_code == 200


async def test_an_archived_project_refuses_status_changes(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    await archive_project(stories_container, project)

    response = await put_test_status(client, project, jira_key, "ready_for_test")
    detail = await client.get(f"/api/projects/{project.key}/stories/{jira_key}")

    assert response.status_code == 409
    assert response.json()["code"] == "PROJECT_ARCHIVED"
    assert detail.json()["availableTestStatuses"] == []


async def test_a_status_change_publishes_story_changed(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    recording_live_event_publisher.events.clear()

    response = await put_test_status(client, project, jira_key.lower(), "ready_for_test")

    assert response.status_code == 200
    assert len(recording_live_event_publisher.events) == 1
    event = recording_live_event_publisher.events[0]
    assert event.type is LiveEventType.STORY_CHANGED
    assert event.project_id == project.id
    assert event.ids == {"storyId": response.json()["id"], "jiraKey": jira_key}


async def test_unknown_stories_and_non_members_are_not_found(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)

    unknown = await put_test_status(client, project, f"{project.key}-404", "ready_for_test")
    await sign_up_member(client, stories_container, recording_mailer, project, None)
    non_member = await put_test_status(client, project, jira_key, "ready_for_test")

    assert unknown.status_code == 404
    assert unknown.json()["message"] == "Story not found."
    assert non_member.status_code == 404
    assert non_member.json()["message"] == "Project not found."


@pytest.mark.parametrize("current", list(StoryTestStatus))
async def test_mark_story_in_test_moves_any_status_to_in_test(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
    recording_live_event_publisher: RecordingLiveEventPublisher,
    current: StoryTestStatus,
) -> None:
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    runner_id = await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.QC)
    await set_test_status(stories_container, project, jira_key, current)
    row = await find_story_row(stories_container, project, jira_key)
    assert row is not None
    recording_live_event_publisher.events.clear()
    now = datetime.now(UTC)

    async with stories_container.database.begin():
        story = await stories_container.mark_story_in_test.execute(project.id, row.id, runner_id, now)

    assert story.test_status is StoryTestStatus.IN_TEST
    stored = await find_story_row(stories_container, project, jira_key)
    assert stored is not None
    assert stored.test_status is StoryTestStatus.IN_TEST
    if current is not StoryTestStatus.IN_TEST:
        assert stored.test_status_changed_by == runner_id
        assert stored.test_status_changed_at == now
    assert recording_live_event_publisher.events == []


async def test_mark_story_in_test_rolls_back_with_the_caller(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project, jira_key = await seed_story(client, stories_container, recording_mailer, fake_jira_client)
    runner_id = await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.QC)
    row = await find_story_row(stories_container, project, jira_key)
    assert row is not None

    with pytest.raises(RuntimeError):
        async with stories_container.database.begin():
            await stories_container.mark_story_in_test.execute(project.id, row.id, runner_id, datetime.now(UTC))
            raise RuntimeError("run start failed")

    stored = await find_story_row(stories_container, project, jira_key)
    assert stored is not None
    assert stored.test_status is StoryTestStatus.NOT_STARTED


async def test_mark_story_in_test_refuses_an_unknown_story(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project, _ = await seed_story(client, stories_container, recording_mailer, fake_jira_client)

    with pytest.raises(StoryNotFoundError):
        await stories_container.mark_story_in_test.execute(project.id, project.id, project.id, datetime.now(UTC))

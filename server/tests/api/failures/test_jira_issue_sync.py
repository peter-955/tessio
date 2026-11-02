from uuid import UUID

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.failures import FailureStatus
from app.modules.jira import JiraCredentials, JiraIssueStatus, JiraPermission, JiraUnreachableError
from app.modules.jira.infrastructure import JiraConnectionTable
from app.modules.stories import SyncJiraProjectJobHandler
from app.modules.stories.infrastructure import ProjectSyncStateTable
from app.modules.stories.typing.enums import ProjectSyncStatus
from app.shared.events import LiveEventType
from tests.api.failures.failure_steps import set_failure_status
from tests.api.failures.jira_bug_steps import (
    JiraBugScenario,
    find_failure_row,
    get_fake_jira_client,
    seed_jira_bug_scenario,
    set_failure_jira_issue,
)
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def run_sync(container: Container, project_id: UUID) -> None:
    await SyncJiraProjectJobHandler(container.sync_jira_project).handle({"projectId": str(project_id)})


async def seed_linked_bug(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[JiraBugScenario, str]:
    bug = await seed_jira_bug_scenario(client, container, recording_mailer)
    issue_key = f"{bug.scenario.project.key}-77"
    await set_failure_jira_issue(container, bug.failure_id, issue_key)
    return bug, issue_key


def set_jira_status(container: Container, issue_key: str, status_name: str, is_done: bool) -> None:
    get_fake_jira_client(container).statuses_by_key[issue_key] = JiraIssueStatus(
        key=issue_key, status_name=status_name, is_done=is_done
    )


async def find_sync_status(container: Container, project_id: UUID) -> ProjectSyncStatus:
    async with container.database.begin():
        row = await container.database.get_current_session().get(
            ProjectSyncStateTable, project_id, populate_existing=True
        )
    assert row is not None
    return row.status


async def test_the_sync_shows_done_in_jira_but_never_changes_the_failure_status(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    bug, issue_key = await seed_linked_bug(client, container, recording_mailer)
    set_jira_status(container, issue_key, "Done", is_done=True)
    recording_live_event_publisher.events.clear()

    await run_sync(container, bug.scenario.project.id)

    row = await find_failure_row(container, bug.failure_id)
    assert row.jira_issue_status == "Done"
    assert row.jira_issue_done_at is not None
    assert row.status == FailureStatus.OPEN
    assert get_fake_jira_client(container).status_requests == [[issue_key]]
    changed = [
        event.ids["failureId"]
        for event in recording_live_event_publisher.events
        if event.type is LiveEventType.FAILURE_CHANGED
    ]
    assert changed == [str(bug.failure_id)]
    detail = await client.get(f"/api/projects/{bug.scenario.project.key}/failures/{bug.failure_id}")
    assert detail.json()["isDoneInJira"] is True
    assert detail.json()["jiraIssueStatus"] == "Done"
    assert detail.json()["status"] == "open"


async def test_a_reopened_jira_issue_clears_done_in_jira(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    bug, issue_key = await seed_linked_bug(client, container, recording_mailer)
    set_jira_status(container, issue_key, "Done", is_done=True)
    await run_sync(container, bug.scenario.project.id)
    done_at = (await find_failure_row(container, bug.failure_id)).jira_issue_done_at
    await run_sync(container, bug.scenario.project.id)
    unchanged_done_at = (await find_failure_row(container, bug.failure_id)).jira_issue_done_at
    set_jira_status(container, issue_key, "Reopened", is_done=False)

    await run_sync(container, bug.scenario.project.id)

    row = await find_failure_row(container, bug.failure_id)
    assert done_at is not None
    assert unchanged_done_at == done_at
    assert row.jira_issue_status == "Reopened"
    assert row.jira_issue_done_at is None


async def test_verified_failures_are_not_refreshed(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    bug, issue_key = await seed_linked_bug(client, container, recording_mailer)
    await set_failure_status(container, bug.failure_id, FailureStatus.VERIFIED)
    set_jira_status(container, issue_key, "Done", is_done=True)

    await run_sync(container, bug.scenario.project.id)

    assert get_fake_jira_client(container).status_requests == []
    assert (await find_failure_row(container, bug.failure_id)).jira_issue_status == "To Do"


async def test_an_unreachable_status_search_does_not_fail_the_sync(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    bug, _ = await seed_linked_bug(client, container, recording_mailer)

    async def list_issue_statuses(credentials: JiraCredentials, issue_keys: list[str]) -> list[JiraIssueStatus]:
        raise JiraUnreachableError

    monkeypatch.setattr(get_fake_jira_client(container), "list_issue_statuses", list_issue_statuses)

    await run_sync(container, bug.scenario.project.id)

    assert await find_sync_status(container, bug.scenario.project.id) is ProjectSyncStatus.SUCCEEDED
    assert (await find_failure_row(container, bug.failure_id)).jira_issue_status == "To Do"


async def test_each_sync_refreshes_the_write_access_check(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    bug, _ = await seed_linked_bug(client, container, recording_mailer)
    get_fake_jira_client(container).missing_permissions_by_project_key[bug.scenario.project.key] = frozenset(
        {JiraPermission.ADD_COMMENTS}
    )

    await run_sync(container, bug.scenario.project.id)

    async with container.database.begin():
        row = await container.database.get_current_session().get(JiraConnectionTable, 1, populate_existing=True)
    assert row is not None
    assert row.can_create_issues is True
    assert row.can_comment is False
    assert row.missing_permissions == ["ADD_COMMENTS"]
    assert row.permissions_checked_at is not None

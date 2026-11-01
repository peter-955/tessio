from uuid import UUID, uuid7

import pytest
from httpx import AsyncClient
from pydantic import JsonValue

from app.modules.jira import JiraCredentials, JiraIssue, JiraSprintState
from app.modules.stories import SyncJiraProjectJobHandler
from app.modules.stories import TestStatus as StoryTestStatus
from app.modules.stories.typing.enums import ProjectSyncStatus
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from app.shared.typing.enums import ErrorCode
from tests.api.stories.conftest import StoriesTestContainer
from tests.api.stories.story_steps import (
    build_closed_sprint,
    build_issue,
    build_sprint,
    clear_jira_connection,
    find_story_row,
    list_criterion_rows,
    list_sprint_rows,
    run_sync,
    seed_jira_connection,
    set_board,
    set_test_status,
)
from tests.api.test_data.project_steps import SeededProject, archive_project, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.fakes.fake_jira_client import FakeJiraClient
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


class BrokenJiraClient(FakeJiraClient):
    async def search_issues(self, credentials: JiraCredentials, jql: str) -> list[JiraIssue]:
        raise RuntimeError("unexpected Jira payload")


async def set_up_project(
    client: AsyncClient, stories_container: StoriesTestContainer, recording_mailer: RecordingMailer
) -> tuple[SeededProject, UUID]:
    project = await seed_project(stories_container)
    user_id = await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.ADMIN)
    await seed_jira_connection(stories_container, user_id)
    return project, user_id


async def read_sync_state(client: AsyncClient, project: SeededProject) -> dict[str, JsonValue]:
    response = await client.get(f"/api/projects/{project.key}/sync")
    assert response.status_code == 200
    body: dict[str, JsonValue] = response.json()
    return body


async def test_the_sync_stores_in_scope_sprints_and_refreshes_known_ones(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project, _ = await set_up_project(client, stories_container, recording_mailer)
    active = build_sprint(1, JiraSprintState.ACTIVE)
    future = build_sprint(2, JiraSprintState.FUTURE)
    recently_closed = build_closed_sprint(3, closed_days_ago=10, name="Sprint 3")
    old_closed = build_closed_sprint(4, closed_days_ago=40)
    set_board(
        fake_jira_client,
        project,
        {
            active: [build_issue(project.key, 1)],
            future: [],
            recently_closed: [build_issue(project.key, 3)],
            old_closed: [build_issue(project.key, 4)],
        },
    )
    await run_sync(stories_container, project.id)
    assert [row.jira_sprint_id for row in await list_sprint_rows(stories_container, project)] == [1, 2, 3]
    stored_story = await find_story_row(stories_container, project, f"{project.key}-3")
    assert stored_story is not None
    assert await find_story_row(stories_container, project, f"{project.key}-4") is None

    renamed_old = build_closed_sprint(3, closed_days_ago=45, name="Sprint 3 renamed")
    set_board(
        fake_jira_client,
        project,
        {active: [build_issue(project.key, 1)], future: [], renamed_old: [], old_closed: []},
    )
    await run_sync(stories_container, project.id)

    rows = await list_sprint_rows(stories_container, project)
    assert [row.jira_sprint_id for row in rows] == [1, 2, 3]
    assert rows[2].name == "Sprint 3 renamed"
    assert rows[2].complete_at == renamed_old.complete_at
    refreshed_story = await find_story_row(stories_container, project, f"{project.key}-3")
    assert refreshed_story is not None
    assert refreshed_story.jira_missing_at is None


async def test_the_sync_skips_epics_and_sub_tasks_and_prefers_the_active_sprint(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project, _ = await set_up_project(client, stories_container, recording_mailer)
    active = build_sprint(1, JiraSprintState.ACTIVE, name="Checkout")
    closed = build_closed_sprint(2, closed_days_ago=3)
    carried_over = build_issue(project.key, 1, criteria=["Pay by card", "See receipt"], summary="Pay for an order")
    set_board(
        fake_jira_client,
        project,
        {
            active: [
                carried_over,
                build_issue(project.key, 2, issue_type_name="Epic"),
                build_issue(project.key, 3, issue_type_name="Sub-task", is_subtask=True),
            ],
            closed: [carried_over],
        },
    )

    await run_sync(stories_container, project.id)

    stories = (await client.get(f"/api/projects/{project.key}/stories")).json()
    assert [story["jiraKey"] for story in stories] == [f"{project.key}-1"]
    story = stories[0]
    assert story["sprintName"] == "Checkout"
    assert story["jiraUrl"] == f"https://team.atlassian.net/browse/{project.key}-1"
    assert story["title"] == "Pay for an order"
    assert story["testStatus"] == "not_started"
    assert story["criterionCount"] == 2
    assert story["jiraIssueType"] == "Story"
    assert story["jiraStatus"] == "In Progress"
    detail = (await client.get(f"/api/projects/{project.key}/stories/{project.key}-1")).json()
    assert [(criterion["code"], criterion["text"]) for criterion in detail["criteria"]] == [
        ("AC1", "Pay by card"),
        ("AC2", "See receipt"),
    ]
    state = await read_sync_state(client, project)
    assert state["status"] == "succeeded"
    assert state["finishedAt"] is not None
    assert state["lastSucceededAt"] == state["finishedAt"]
    assert state["errorCode"] is None
    finished_events = [
        event for event in recording_live_event_publisher.events if event.type is LiveEventType.JIRA_SYNC_FINISHED
    ]
    assert len(finished_events) == 1
    assert finished_events[0].project_id == project.id
    assert finished_events[0].ids == {"projectKey": project.key}
    assert stories_container.recording_criteria_changed_handler.changes == []


async def test_a_re_sync_flags_changed_and_removed_criteria_and_keeps_the_test_status(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project, _ = await set_up_project(client, stories_container, recording_mailer)
    active = build_sprint(1)
    jira_key = f"{project.key}-1"
    set_board(fake_jira_client, project, {active: [build_issue(project.key, 1, criteria=["A", "B", "C"])]})
    await run_sync(stories_container, project.id)
    await set_test_status(stories_container, project, jira_key, StoryTestStatus.READY_FOR_TEST)
    story = await find_story_row(stories_container, project, jira_key)
    assert story is not None
    original_rows = await list_criterion_rows(stories_container, story.id)

    set_board(
        fake_jira_client,
        project,
        {active: [build_issue(project.key, 1, criteria=["A", "B changed"], summary="Renamed")]},
    )
    await run_sync(stories_container, project.id)

    changes = stories_container.recording_criteria_changed_handler.changes
    assert len(changes) == 1
    assert changes[0].project_id == project.id
    assert changes[0].story_id == story.id
    assert changes[0].changed_criterion_ids == {original_rows[1].id}
    assert changes[0].removed_criterion_ids == {original_rows[2].id}
    assert changes[0].added_criterion_ids == frozenset()
    rows = await list_criterion_rows(stories_container, story.id)
    assert [(row.id, row.text, row.removed_at is None) for row in rows] == [
        (original_rows[0].id, "A", True),
        (original_rows[1].id, "B changed", True),
        (original_rows[2].id, "C", False),
    ]
    resynced = await find_story_row(stories_container, project, jira_key)
    assert resynced is not None
    assert resynced.id == story.id
    assert resynced.title == "Renamed"
    assert resynced.test_status is StoryTestStatus.READY_FOR_TEST
    summary = (await client.get(f"/api/projects/{project.key}/stories")).json()[0]
    assert summary["criterionCount"] == 2


async def test_a_story_gone_from_its_sprint_is_flagged_missing_until_it_returns(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project, _ = await set_up_project(client, stories_container, recording_mailer)
    active = build_sprint(1)
    kept = build_issue(project.key, 1)
    leaving = build_issue(project.key, 2)
    set_board(fake_jira_client, project, {active: [kept, leaving]})
    await run_sync(stories_container, project.id)

    set_board(fake_jira_client, project, {active: [kept]})
    await run_sync(stories_container, project.id)

    missing = await find_story_row(stories_container, project, leaving.key)
    assert missing is not None
    assert missing.jira_missing_at is not None
    assert missing.sprint_id is not None
    present = await find_story_row(stories_container, project, kept.key)
    assert present is not None
    assert present.jira_missing_at is None
    sprints = (await client.get(f"/api/projects/{project.key}/sprints")).json()
    assert sprints[0]["storyCount"] == 1
    listed = (await client.get(f"/api/projects/{project.key}/stories")).json()
    assert [story["jiraMissingAt"] is not None for story in listed] == [False, True]

    set_board(fake_jira_client, project, {active: [kept, leaving]})
    await run_sync(stories_container, project.id)

    returned = await find_story_row(stories_container, project, leaving.key)
    assert returned is not None
    assert returned.jira_missing_at is None


async def test_an_unreachable_jira_fails_the_sync(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project, _ = await set_up_project(client, stories_container, recording_mailer)
    set_board(fake_jira_client, project, {build_sprint(1): [build_issue(project.key, 1)]})
    fake_jira_client.is_unreachable = True

    await run_sync(stories_container, project.id)

    state = await read_sync_state(client, project)
    assert state["status"] == "failed"
    assert state["errorCode"] == "JIRA_UNREACHABLE"
    assert state["finishedAt"] is not None
    assert state["lastSucceededAt"] is None
    failed_events = [
        event for event in recording_live_event_publisher.events if event.type is LiveEventType.JIRA_SYNC_FAILED
    ]
    assert len(failed_events) == 1
    assert failed_events[0].ids == {"projectKey": project.key, "errorCode": "JIRA_UNREACHABLE"}
    assert (await client.get(f"/api/projects/{project.key}/stories")).json() == []


async def test_a_sync_without_a_jira_connection_fails(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    project, _ = await set_up_project(client, stories_container, recording_mailer)
    await clear_jira_connection(stories_container)

    await run_sync(stories_container, project.id)

    state = await read_sync_state(client, project)
    assert state["status"] == "failed"
    assert state["errorCode"] == "JIRA_NOT_CONFIGURED"
    assert [event.ids.get("errorCode") for event in recording_live_event_publisher.events] == ["JIRA_NOT_CONFIGURED"]


async def test_an_archived_project_is_not_synced(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project, _ = await set_up_project(client, stories_container, recording_mailer)
    set_board(fake_jira_client, project, {build_sprint(1): [build_issue(project.key, 1)]})
    await archive_project(stories_container, project)

    await run_sync(stories_container, project.id)

    state = await read_sync_state(client, project)
    assert state["status"] == "failed"
    assert state["errorCode"] == "PROJECT_ARCHIVED"
    assert fake_jira_client.requested_site_urls == []
    assert (await client.get(f"/api/projects/{project.key}/stories")).json() == []


async def test_an_unexpected_error_fails_the_sync_and_is_raised_for_a_retry(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    broken_jira_client = BrokenJiraClient()
    broken_jira_client.sprints_by_board_id[1] = [build_sprint(1)]
    stories_container.__dict__["jira_client"] = broken_jira_client
    project, _ = await set_up_project(client, stories_container, recording_mailer)

    with pytest.raises(RuntimeError):
        await run_sync(stories_container, project.id)

    state = await read_sync_state(client, project)
    assert state["status"] == "failed"
    assert state["errorCode"] is None
    assert [event.type for event in recording_live_event_publisher.events] == [LiveEventType.JIRA_SYNC_FAILED]
    assert recording_live_event_publisher.events[0].ids == {"projectKey": project.key}


@pytest.mark.parametrize("data", [{}, {"projectId": "not-a-uuid"}, {"projectId": 42}, {"projectId": str(uuid7())}])
async def test_invalid_job_data_does_nothing(
    stories_container: StoriesTestContainer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
    data: dict[str, JsonValue],
) -> None:
    await SyncJiraProjectJobHandler(stories_container.sync_jira_project).handle(data)

    assert recording_live_event_publisher.events == []


async def test_the_failed_error_code_is_a_known_code(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project, _ = await set_up_project(client, stories_container, recording_mailer)
    fake_jira_client.valid_api_token = "rotated-token"

    await run_sync(stories_container, project.id)

    async with stories_container.database.begin():
        state = await stories_container.project_sync_state_repository.find(project.id)
    assert state is not None
    assert state.status is ProjectSyncStatus.FAILED
    assert state.error_code is ErrorCode.JIRA_INVALID_CREDENTIALS

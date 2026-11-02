from datetime import UTC, datetime, timedelta
from uuid import uuid7

import pytest
from httpx import AsyncClient

from app.modules.jira import JiraSprintState
from app.modules.stories import TestStatus as StoryTestStatus
from app.shared.permissions import ProjectRole
from tests.api.stories.conftest import StoriesTestContainer
from tests.api.stories.story_steps import (
    build_closed_sprint,
    build_issue,
    build_sprint,
    detach_story_from_sprint,
    find_story_row,
    run_sync,
    seed_jira_connection,
    set_board,
    set_project_board_id,
    set_test_status,
)
from tests.api.test_data.project_steps import SeededProject, add_member, seed_project, sign_up_member
from tests.conftest import RecordingMailer
from tests.fakes.fake_jira_client import FakeJiraClient

EXPECTED_STATUSES_FROM_IN_TEST_BY_ROLE = {
    ProjectRole.ADMIN: ["passed", "failed"],
    ProjectRole.PM: [],
    ProjectRole.BA: [],
    ProjectRole.QC: ["passed", "failed"],
    ProjectRole.DEV: [],
    ProjectRole.VIEWER: [],
}


async def seed_synced_project(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> SeededProject:
    project = await seed_project(stories_container)
    admin_id = await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.ADMIN)
    await seed_jira_connection(stories_container, admin_id)
    now = datetime.now(UTC)
    set_board(
        fake_jira_client,
        project,
        {
            build_closed_sprint(1, closed_days_ago=20, name="Closed earlier"): [
                build_issue(project.key, 10, summary="Archive 50% of orders")
            ],
            build_sprint(2, JiraSprintState.FUTURE, name="Future late", start_at=now + timedelta(days=10)): [],
            build_closed_sprint(3, closed_days_ago=5, name="Closed later"): [],
            build_sprint(4, JiraSprintState.FUTURE, name="Future undated"): [],
            build_sprint(5, JiraSprintState.ACTIVE, name="Current"): [
                build_issue(
                    project.key, 2, criteria=["Pay by card", "See receipt", "Email receipt"], summary="Checkout"
                ),
                build_issue(project.key, 1, criteria=["Sign in"], summary="Sign in with email"),
            ],
            build_sprint(6, JiraSprintState.FUTURE, name="Future early", start_at=now + timedelta(days=2)): [],
        },
    )
    await run_sync(stories_container, project.id)
    return project


async def test_sprints_are_listed_active_then_future_then_closed_with_counts(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project = await seed_synced_project(client, stories_container, recording_mailer, fake_jira_client)

    response = await client.get(f"/api/projects/{project.key}/sprints")

    assert response.status_code == 200
    sprints = response.json()
    assert [(sprint["name"], sprint["state"], sprint["storyCount"]) for sprint in sprints] == [
        ("Current", "active", 2),
        ("Future early", "future", 0),
        ("Future late", "future", 0),
        ("Future undated", "future", 0),
        ("Closed later", "closed", 0),
        ("Closed earlier", "closed", 1),
    ]
    assert sprints[0].keys() == {
        "id",
        "jiraSprintId",
        "name",
        "state",
        "startAt",
        "endAt",
        "completeAt",
        "storyCount",
        "syncedAt",
    }
    detail = await client.get(f"/api/projects/{project.key}/sprints/{sprints[0]['id']}")
    assert detail.status_code == 200
    assert detail.json() == sprints[0]


async def test_an_unknown_sprint_is_not_found(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project = await seed_synced_project(client, stories_container, recording_mailer, fake_jira_client)

    response = await client.get(f"/api/projects/{project.key}/sprints/{uuid7()}")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


async def test_sprints_and_stories_of_another_project_are_not_reachable(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project = await seed_project(stories_container)
    other_project = await seed_project(stories_container)
    other_board_id = 2
    await set_project_board_id(stories_container, other_project, other_board_id)
    admin_id = await sign_up_member(client, stories_container, recording_mailer, project, ProjectRole.ADMIN)
    await add_member(stories_container, other_project, admin_id, ProjectRole.ADMIN)
    await seed_jira_connection(stories_container, admin_id)
    current = build_sprint(5, JiraSprintState.ACTIVE, name="Current")
    set_board(fake_jira_client, project, {current: [build_issue(project.key, 1, criteria=["Sign in"])]})
    set_board(
        fake_jira_client,
        other_project,
        {
            build_sprint(50, JiraSprintState.ACTIVE, name="Other current"): [
                build_issue(other_project.key, 1, criteria=["Pay"]),
                build_issue(other_project.key, 2, criteria=["Refund"]),
            ]
        },
        board_id=other_board_id,
    )
    await run_sync(stories_container, project.id)
    await run_sync(stories_container, other_project.id)
    other_sprint_id = (await client.get(f"/api/projects/{other_project.key}/sprints")).json()[0]["id"]
    other_story_key = f"{other_project.key}-1"
    detached_story_key = f"{other_project.key}-2"
    await detach_story_from_sprint(stories_container, other_project, detached_story_key)
    project_url = f"/api/projects/{project.key}"

    sprint = await client.get(f"{project_url}/sprints/{other_sprint_id}")
    story = await client.get(f"{project_url}/stories/{other_story_key}")
    test_status = await client.put(
        f"{project_url}/stories/{other_story_key}/test-status", json={"testStatus": "ready_for_test"}
    )
    stories_in_other_sprint = await client.get(f"{project_url}/stories", params={"sprintId": other_sprint_id})

    assert [sprint.status_code, story.status_code, test_status.status_code] == [404, 404, 404]
    assert stories_in_other_sprint.status_code == 200
    assert stories_in_other_sprint.json() == []
    set_board(fake_jira_client, project, {current: []})
    await run_sync(stories_container, project.id)
    own_story = await find_story_row(stories_container, project, f"{project.key}-1")
    assert own_story is not None
    assert own_story.jira_missing_at is not None
    for jira_key in [other_story_key, detached_story_key]:
        other_story = await find_story_row(stories_container, other_project, jira_key)
        assert other_story is not None
        assert other_story.jira_missing_at is None
        assert other_story.test_status is StoryTestStatus.NOT_STARTED


async def test_stories_are_filtered_by_sprint_status_and_query(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project = await seed_synced_project(client, stories_container, recording_mailer, fake_jira_client)
    await set_test_status(stories_container, project, f"{project.key}-2", StoryTestStatus.READY_FOR_TEST)
    sprints = (await client.get(f"/api/projects/{project.key}/sprints")).json()
    current_sprint_id = sprints[0]["id"]
    stories_url = f"/api/projects/{project.key}/stories"

    async def list_keys(params: dict[str, str]) -> list[str]:
        response = await client.get(stories_url, params=params)
        assert response.status_code == 200
        return [story["jiraKey"].removeprefix(f"{project.key}-") for story in response.json()]

    assert await list_keys({}) == ["1", "2", "10"]
    assert await list_keys({"sprintId": current_sprint_id}) == ["1", "2"]
    assert await list_keys({"testStatus": "ready_for_test"}) == ["2"]
    assert await list_keys({"sprintId": current_sprint_id, "testStatus": "not_started"}) == ["1"]
    assert await list_keys({"query": "checkOUT"}) == ["2"]
    assert await list_keys({"query": f"{project.key.lower()}-1"}) == ["1", "10"]
    assert await list_keys({"query": "50%"}) == ["10"]
    assert await list_keys({"query": "%"}) == ["10"]
    assert await list_keys({"query": "   "}) == ["1", "2", "10"]
    first = (await client.get(stories_url, params={"query": "Checkout"})).json()[0]
    assert first["sprintId"] == current_sprint_id
    assert first["sprintName"] == "Current"
    assert first["criterionCount"] == 3
    too_long = await client.get(stories_url, params={"query": "x" * 101})
    assert too_long.status_code == 422
    unknown_status = await client.get(stories_url, params={"testStatus": "done"})
    assert unknown_status.status_code == 422


async def test_the_story_detail_includes_removed_criteria_and_the_available_statuses(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project = await seed_synced_project(client, stories_container, recording_mailer, fake_jira_client)
    current = build_sprint(5, JiraSprintState.ACTIVE, name="Current")
    set_board(
        fake_jira_client,
        project,
        {current: [build_issue(project.key, 2, criteria=["Pay by card"], summary="Checkout")]},
    )
    await run_sync(stories_container, project.id)

    response = await client.get(f"/api/projects/{project.key}/stories/{project.key.lower()}-2")

    assert response.status_code == 200
    detail = response.json()
    assert detail.keys() == {
        "id",
        "jiraKey",
        "jiraUrl",
        "title",
        "jiraStatus",
        "jiraIssueType",
        "testStatus",
        "syncedAt",
        "jiraMissingAt",
        "description",
        "sprint",
        "criteria",
        "availableTestStatuses",
        "testStatusChangedAt",
        "jiraUpdatedAt",
        "source",
        "descriptionText",
    }
    assert detail["source"] == "jira"
    assert detail["descriptionText"] is None
    assert detail["jiraKey"] == f"{project.key}-2"
    assert detail["sprint"]["name"] == "Current"
    assert detail["sprint"]["state"] == "active"
    assert detail["description"]["type"] == "doc"
    assert [
        (criterion["code"], criterion["position"], criterion["text"], criterion["isRemoved"])
        for criterion in detail["criteria"]
    ] == [("AC1", 1, "Pay by card", False), ("AC2", 2, "See receipt", True), ("AC3", 3, "Email receipt", True)]
    assert detail["criteria"][1]["removedAt"] is not None
    assert detail["availableTestStatuses"] == ["ready_for_test"]
    assert detail["testStatusChangedAt"] is None


@pytest.mark.parametrize("role", list(ProjectRole))
async def test_every_role_can_read_sprints_and_stories(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
    role: ProjectRole,
) -> None:
    project = await seed_synced_project(client, stories_container, recording_mailer, fake_jira_client)
    await set_test_status(stories_container, project, f"{project.key}-1", StoryTestStatus.IN_TEST)
    await sign_up_member(client, stories_container, recording_mailer, project, role)

    sprints = await client.get(f"/api/projects/{project.key}/sprints")
    stories = await client.get(f"/api/projects/{project.key}/stories")
    detail = await client.get(f"/api/projects/{project.key}/stories/{project.key}-1")
    sync_state = await client.get(f"/api/projects/{project.key}/sync")

    assert sprints.status_code == 200
    assert len(sprints.json()) == 6
    assert stories.status_code == 200
    assert len(stories.json()) == 3
    assert detail.status_code == 200
    assert detail.json()["availableTestStatuses"] == EXPECTED_STATUSES_FROM_IN_TEST_BY_ROLE[role]
    assert sync_state.json()["status"] == "succeeded"


async def test_an_unknown_story_is_not_found(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project = await seed_synced_project(client, stories_container, recording_mailer, fake_jira_client)

    response = await client.get(f"/api/projects/{project.key}/stories/{project.key}-999")

    assert response.status_code == 404
    assert response.json() == {"code": "NOT_FOUND", "message": "Story not found."}


async def test_a_non_member_cannot_read_stories(
    client: AsyncClient,
    stories_container: StoriesTestContainer,
    recording_mailer: RecordingMailer,
    fake_jira_client: FakeJiraClient,
) -> None:
    project = await seed_synced_project(client, stories_container, recording_mailer, fake_jira_client)
    await sign_up_member(client, stories_container, recording_mailer, project, None)

    responses = [
        await client.get(f"/api/projects/{project.key}/sprints"),
        await client.get(f"/api/projects/{project.key}/stories"),
        await client.get(f"/api/projects/{project.key}/stories/{project.key}-1"),
    ]

    assert [response.status_code for response in responses] == [404, 404, 404]
    assert all(response.json()["message"] == "Project not found." for response in responses)

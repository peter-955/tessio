from uuid import UUID

import pytest
from httpx import AsyncClient, Response

from app.container import Container
from app.modules.projects.infrastructure import StaticJiraConnectionChecker
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import seed_test_case
from tests.api.projects.user_steps import (
    SignedUpAccount,
    build_create_project_body,
    generate_project_key,
    sign_up_as,
    use_session,
)
from tests.api.stories.conftest import StoriesTestContainer
from tests.api.test_data.project_steps import SeededProject, add_member, seed_project
from tests.conftest import RecordingMailer


async def create_project_without_jira(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[SignedUpAccount, str]:
    container.__dict__["jira_connection_checker"] = StaticJiraConnectionChecker(is_configured=False)
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN, "Ada Admin")
    project_key = generate_project_key()
    response = await client.post("/api/projects", json={"key": project_key, "name": "No Jira"})
    assert response.status_code == 201, response.text
    return admin, project_key


async def write_story(client: AsyncClient, project_key: str, **body: object) -> Response:
    return await client.post(
        f"/api/projects/{project_key}/stories",
        json={
            "title": "Pay by card",
            "description": "As a buyer\n\nI pay by card",
            "criteria": ["Card accepted"],
            **body,
        },
    )


async def test_a_project_without_jira_can_be_created_without_a_jira_connection(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, project_key = await create_project_without_jira(client, container, recording_mailer)

    project = (await client.get(f"/api/projects/{project_key}")).json()

    assert (project["jiraProjectKey"], project["jiraBoardId"], project["isLinkedToJira"]) == (None, None, False)


async def test_a_project_needs_both_jira_fields_or_neither(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    body = build_create_project_body()
    del body["jiraBoardId"]

    response = await client.post("/api/projects", json=body)

    assert response.status_code == 422


async def test_a_project_without_jira_has_nothing_to_sync_and_no_board(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, project_key = await create_project_without_jira(client, container, recording_mailer)

    sync = await client.post(f"/api/projects/{project_key}/sync")
    board = await client.patch(f"/api/projects/{project_key}", json={"jiraBoardId": 3})

    assert (sync.status_code, sync.json()["code"]) == (409, "JIRA_NOT_CONFIGURED")
    assert (board.status_code, board.json()["code"]) == (409, "JIRA_NOT_CONFIGURED")


async def test_written_stories_get_project_keys_and_numbered_criteria(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, project_key = await create_project_without_jira(client, container, recording_mailer)

    first = await write_story(client, project_key, criteria=["Card accepted", "  Receipt sent  "])
    second = await write_story(client, project_key, title="Refund", description=None, criteria=[])
    listed = (await client.get(f"/api/projects/{project_key}/stories")).json()

    assert first.status_code == 201, first.text
    detail = first.json()
    assert (detail["jiraKey"], detail["source"], detail["jiraUrl"], detail["jiraStatus"]) == (
        f"{project_key}-1",
        "tessio",
        "",
        "",
    )
    assert detail["descriptionText"] == "As a buyer\n\nI pay by card"
    assert [(criterion["code"], criterion["text"]) for criterion in detail["criteria"]] == [
        ("AC1", "Card accepted"),
        ("AC2", "Receipt sent"),
    ]
    assert (second.json()["jiraKey"], second.json()["description"], second.json()["descriptionText"]) == (
        f"{project_key}-2",
        None,
        "",
    )
    assert sorted((story["jiraKey"], story["source"]) for story in listed) == [
        (f"{project_key}-1", "tessio"),
        (f"{project_key}-2", "tessio"),
    ]


async def test_editing_criteria_flags_the_changed_and_removed_ones(
    client: AsyncClient, stories_container: StoriesTestContainer, recording_mailer: RecordingMailer
) -> None:
    _, project_key = await create_project_without_jira(client, stories_container, recording_mailer)
    created = (
        await write_story(client, project_key, criteria=["Card accepted", "Receipt sent", "Invoice stored"])
    ).json()
    ids_by_code = {criterion["code"]: criterion["id"] for criterion in created["criteria"]}

    response = await client.patch(
        f"/api/projects/{project_key}/stories/{project_key.lower()}-1",
        json={"title": "Pay by card or voucher", "criteria": ["Card accepted", "Receipt emailed"]},
    )

    assert response.status_code == 200, response.text
    updated = response.json()
    assert updated["title"] == "Pay by card or voucher"
    assert updated["descriptionText"] == ""
    assert [(criterion["code"], criterion["text"], criterion["isRemoved"]) for criterion in updated["criteria"]] == [
        ("AC1", "Card accepted", False),
        ("AC2", "Receipt emailed", False),
        ("AC3", "Invoice stored", True),
    ]
    [change] = stories_container.recording_criteria_changed_handler.changes
    assert {str(criterion_id) for criterion_id in change.changed_criterion_ids} == {ids_by_code["AC2"]}
    assert {str(criterion_id) for criterion_id in change.removed_criterion_ids} == {ids_by_code["AC3"]}


async def test_an_unused_story_can_be_deleted_and_its_key_is_not_reused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, project_key = await create_project_without_jira(client, container, recording_mailer)
    await write_story(client, project_key)

    deleted = await client.delete(f"/api/projects/{project_key}/stories/{project_key}-1")
    missing = await client.get(f"/api/projects/{project_key}/stories/{project_key}-1")
    next_story = await write_story(client, project_key)

    assert deleted.status_code == 204
    assert missing.status_code == 404
    assert next_story.json()["jiraKey"] == f"{project_key}-2"


async def test_a_story_with_test_cases_cannot_be_deleted(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    admin, project_key = await create_project_without_jira(client, container, recording_mailer)
    story = (await write_story(client, project_key)).json()
    project = (await client.get(f"/api/projects/{project_key}")).json()
    seeded = SeededProject(id=UUID(project["id"]), key=project_key)
    await seed_test_case(container, seeded, UUID(story["id"]), 1, admin.user_id)

    response = await client.delete(f"/api/projects/{project_key}/stories/{project_key}-1")

    assert (response.status_code, response.json()["code"]) == (409, "CONFLICT")


async def test_stories_of_a_jira_project_cannot_be_written_in_tessio(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    account = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await add_member(container, project, account.user_id, ProjectRole.BA)

    response = await client.post(f"/api/projects/{project.key}/stories", json={"title": "Pay by card"})

    assert (response.status_code, response.json()["code"]) == (422, "INVALID_REQUEST")


@pytest.mark.parametrize(
    ("role", "status_code"),
    [
        (ProjectRole.QC, 201),
        (ProjectRole.PM, 201),
        (ProjectRole.BA, 201),
        (ProjectRole.DEV, 403),
        (ProjectRole.VIEWER, 403),
    ],
)
async def test_admin_pm_ba_and_qc_write_stories(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    role: ProjectRole,
    status_code: int,
) -> None:
    _, project_key = await create_project_without_jira(client, container, recording_mailer)
    project = (await client.get(f"/api/projects/{project_key}")).json()
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, "Mia Member")
    await add_member(container, SeededProject(id=UUID(project["id"]), key=project_key), member.user_id, role)
    use_session(client, member.session_token)

    response = await write_story(client, project_key)

    assert response.status_code == status_code

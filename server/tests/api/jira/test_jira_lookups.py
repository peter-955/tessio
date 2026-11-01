import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.jira import JiraBoard, JiraNotConfiguredError, JiraProject, LoadJiraCredentialsUseCase
from app.modules.jira.infrastructure import PostgresJiraConnectionRepository
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.jira.jira_steps import (
    JIRA_ACCOUNT_EMAIL,
    JIRA_API_TOKEN,
    JIRA_SITE_URL,
    add_project_member,
    generate_jira_project_key,
    put_jira_connection,
    seed_linked_project,
)
from tests.api.projects.user_steps import sign_up_as, use_session
from tests.conftest import RecordingMailer
from tests.fakes.fake_jira_client import FakeJiraClient


async def test_jira_projects_need_a_connection(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    response = await client.get("/api/workspace/jira/projects")

    assert response.status_code == 409
    assert response.json()["code"] == "JIRA_NOT_CONFIGURED"


async def test_jira_projects_exclude_linked_keys_and_are_sorted_by_name(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    linked_key = generate_jira_project_key()
    archived_linked_key = generate_jira_project_key()
    await seed_linked_project(container, linked_key)
    await seed_linked_project(container, archived_linked_key, is_archived=True)
    fake_jira_client.projects = [
        JiraProject(id="10003", key="ZED", name="zebra"),
        JiraProject(id="10001", key=linked_key, name="Linked"),
        JiraProject(id="10002", key="APP", name="Apple"),
        JiraProject(id="10004", key=archived_linked_key, name="Archived"),
        JiraProject(id="10005", key="BAN", name="banana"),
    ]
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    assert (await put_jira_connection(client)).status_code == 200

    response = await client.get("/api/workspace/jira/projects")

    assert response.status_code == 200
    assert response.json() == [
        {"id": "10002", "key": "APP", "name": "Apple"},
        {"id": "10005", "key": "BAN", "name": "banana"},
        {"id": "10003", "key": "ZED", "name": "zebra"},
    ]


async def test_workspace_members_cannot_list_jira_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    assert (await put_jira_connection(client)).status_code == 200
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)

    response = await client.get("/api/workspace/jira/projects")

    assert response.status_code == 403


async def test_workspace_admins_list_the_boards_of_a_jira_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    fake_jira_client.boards_by_project_key = {
        "SHOP": [JiraBoard(id=9, name="Shop scrum", type="scrum"), JiraBoard(id=3, name="Kanban", type="kanban")]
    }
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    assert (await put_jira_connection(client)).status_code == 200

    response = await client.get("/api/workspace/jira/boards", params={"jiraProjectKey": "SHOP"})
    unknown_response = await client.get("/api/workspace/jira/boards", params={"jiraProjectKey": "NOPE"})

    assert response.status_code == 200
    assert response.json() == [
        {"id": 3, "name": "Kanban", "type": "kanban"},
        {"id": 9, "name": "Shop scrum", "type": "scrum"},
    ]
    assert unknown_response.status_code == 404
    assert unknown_response.json()["code"] == "NOT_FOUND"


async def test_boards_need_a_connection_and_a_project_key(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    not_configured_response = await client.get("/api/workspace/jira/boards", params={"jiraProjectKey": "SHOP"})
    missing_key_response = await client.get("/api/workspace/jira/boards")

    assert not_configured_response.status_code == 409
    assert not_configured_response.json()["code"] == "JIRA_NOT_CONFIGURED"
    assert missing_key_response.status_code == 422


async def test_project_admins_of_the_linked_project_list_its_boards(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    jira_project_key = generate_jira_project_key()
    project_id = await seed_linked_project(container, jira_project_key)
    fake_jira_client.boards_by_project_key = {jira_project_key: [JiraBoard(id=5, name="Board", type="scrum")]}
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    assert (await put_jira_connection(client)).status_code == 200
    project_admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    tester = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    outsider = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await add_project_member(container, project_id, project_admin.user_id, ProjectRole.ADMIN)
    await add_project_member(container, project_id, tester.user_id, ProjectRole.QC)
    params = {"jiraProjectKey": jira_project_key}

    use_session(client, project_admin.session_token)
    project_admin_response = await client.get("/api/workspace/jira/boards", params=params)
    unlinked_response = await client.get("/api/workspace/jira/boards", params={"jiraProjectKey": "OTHER"})
    use_session(client, tester.session_token)
    tester_response = await client.get("/api/workspace/jira/boards", params=params)
    use_session(client, outsider.session_token)
    outsider_response = await client.get("/api/workspace/jira/boards", params=params)

    assert project_admin_response.status_code == 200
    assert project_admin_response.json() == [{"id": 5, "name": "Board", "type": "scrum"}]
    assert unlinked_response.status_code == 403
    assert tester_response.status_code == 403
    assert outsider_response.status_code == 403
    assert outsider_response.json()["code"] == "PERMISSION_DENIED"


async def test_an_unreachable_jira_gives_bad_gateway_for_boards(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    fake_jira_client.boards_by_project_key = {"SHOP": []}
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    assert (await put_jira_connection(client)).status_code == 200
    fake_jira_client.is_unreachable = True

    response = await client.get("/api/workspace/jira/boards", params={"jiraProjectKey": "SHOP"})

    assert response.status_code == 502
    assert response.json()["code"] == "JIRA_UNREACHABLE"


async def test_load_jira_credentials_decrypts_the_stored_token(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    use_case = LoadJiraCredentialsUseCase(
        container.database, PostgresJiraConnectionRepository(container.database), container.secret_cipher
    )
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    with pytest.raises(JiraNotConfiguredError):
        await use_case.execute()
    assert (await put_jira_connection(client)).status_code == 200
    credentials = await use_case.execute()

    assert credentials.site_url == JIRA_SITE_URL
    assert credentials.account_email == JIRA_ACCOUNT_EMAIL
    assert credentials.api_token.get_secret_value() == JIRA_API_TOKEN

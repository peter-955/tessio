from httpx import AsyncClient
from sqlalchemy import update

from app.container import Container
from app.modules.jira import JiraPermission
from app.modules.projects.infrastructure import ProjectTable
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.jira.jira_steps import (
    find_jira_connection_row,
    generate_jira_project_key,
    put_jira_connection,
    seed_linked_project,
)
from tests.api.projects.user_steps import sign_up_as, use_session
from tests.api.test_data.project_steps import SeededProject, add_member, archive_project, seed_project
from tests.conftest import RecordingMailer
from tests.fakes.fake_jira_client import FakeJiraClient


async def test_saving_the_connection_stores_what_the_account_can_write(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    jira_project_key = generate_jira_project_key()
    await seed_linked_project(container, jira_project_key)
    fake_jira_client.missing_permissions_by_project_key[jira_project_key] = frozenset(
        {JiraPermission.ADD_COMMENTS, JiraPermission.CREATE_ATTACHMENTS}
    )

    saved = await put_jira_connection(client)
    fetched = await client.get("/api/workspace/jira")

    assert saved.status_code == 200, saved.text
    body = fetched.json()
    assert body["canCreateIssues"] is True
    assert body["canComment"] is False
    assert body["missingPermissions"] == ["ADD_COMMENTS", "CREATE_ATTACHMENTS"]
    assert body["permissionsCheckedAt"] is not None
    assert jira_project_key in fake_jira_client.permission_checks
    row = await find_jira_connection_row(container)
    assert row is not None
    assert row.can_create_issues is True
    assert row.can_comment is False


async def test_archived_projects_are_not_checked(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    archived_key = generate_jira_project_key()
    await seed_linked_project(container, archived_key, is_archived=True)
    fake_jira_client.missing_permissions_by_project_key[archived_key] = frozenset(JiraPermission)

    saved = await put_jira_connection(client)

    assert saved.status_code == 200
    assert archived_key not in fake_jira_client.permission_checks
    assert saved.json()["canCreateIssues"] is True


async def test_a_project_member_sees_the_jira_write_access_of_the_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, fake_jira_client: FakeJiraClient
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    project = await seed_project(container)
    fake_jira_client.missing_permissions_by_project_key[project.key] = frozenset({JiraPermission.CREATE_ISSUES})
    assert (await put_jira_connection(client)).status_code == 200
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, "Quinn")
    await add_member(container, project, member.user_id, ProjectRole.QC)
    use_session(client, member.session_token)

    response = await client.get(f"/api/projects/{project.key}/jira-write-access")

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["isProjectLinked"] is True
    assert body["isConnectionConfigured"] is True
    assert body["canCreateIssues"] is False
    assert body["canComment"] is True
    assert body["missingPermissions"] == ["CREATE_ISSUES"]


async def test_a_project_without_jira_reports_it_is_not_linked(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    project = await seed_project(container)
    await unlink_project(container, project)
    await add_member(container, project, admin.user_id, ProjectRole.ADMIN)

    response = await client.get(f"/api/projects/{project.key}/jira-write-access")

    assert response.status_code == 200
    assert response.json() == {
        "isProjectLinked": False,
        "isConnectionConfigured": False,
        "canCreateIssues": None,
        "canComment": None,
        "missingPermissions": [],
        "checkedAt": None,
    }


async def test_an_archived_project_still_shows_its_write_access(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    project = await seed_project(container)
    await add_member(container, project, admin.user_id, ProjectRole.VIEWER)
    await archive_project(container, project)

    response = await client.get(f"/api/projects/{project.key}/jira-write-access")

    assert response.status_code == 200


async def unlink_project(container: Container, project: SeededProject) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(ProjectTable).where(ProjectTable.id == project.id).values(jira_project_key=None, jira_board_id=None)
        )

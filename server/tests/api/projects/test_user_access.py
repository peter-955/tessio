from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import build_create_project_body, sign_up_as, use_session
from tests.conftest import RecordingMailer


async def test_workspace_admin_sees_a_users_project_access(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    active_body = build_create_project_body()
    archived_body = build_create_project_body()
    await client.post("/api/projects", json=active_body)
    await client.post("/api/projects", json=archived_body)
    developer = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    await client.post("/api/projects", json=build_create_project_body())
    use_session(client, admin.session_token)
    await client.put(f"/api/projects/{active_body['key']}/members/{developer.user_id}", json={"role": "dev"})
    await client.put(f"/api/projects/{archived_body['key']}/members/{developer.user_id}", json={"role": "viewer"})
    await client.post(f"/api/projects/{archived_body['key']}/archive")

    response = await client.get(f"/api/users/{developer.user_id}/access")

    assert response.status_code == 200
    assert sorted((access["projectKey"], access["role"], access["isArchived"]) for access in response.json()) == sorted(
        [(active_body["key"], "dev", False), (archived_body["key"], "viewer", True)]
    )


async def test_workspace_member_cannot_see_user_access(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)

    response = await client.get(f"/api/users/{member.user_id}/access")

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


async def test_unknown_user_access_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    response = await client.get("/api/users/00000000-0000-7000-8000-000000000000/access")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"

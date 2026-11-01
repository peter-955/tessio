from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import sign_up_as, use_session
from tests.conftest import RecordingMailer


async def test_owner_promotes_a_member_to_admin(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)

    promote_response = await client.put(f"/api/users/{member.user_id}/workspace-role", json={"workspaceRole": "admin"})
    repeat_response = await client.put(f"/api/users/{member.user_id}/workspace-role", json={"workspaceRole": "admin"})
    use_session(client, member.session_token)
    promoted_me_response = await client.get("/api/auth/me")
    use_session(client, owner.session_token)
    demote_response = await client.put(f"/api/users/{member.user_id}/workspace-role", json={"workspaceRole": "member"})

    assert promote_response.status_code == 200
    assert promote_response.json()["workspaceRole"] == "admin"
    assert repeat_response.status_code == 200
    assert promoted_me_response.json()["workspaceRole"] == "admin"
    assert demote_response.json()["workspaceRole"] == "member"


async def test_admin_cannot_change_workspace_roles(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    response = await client.put(f"/api/users/{member.user_id}/workspace-role", json={"workspaceRole": "admin"})

    assert response.status_code == 403
    assert response.json()["code"] == "OWNER_ONLY"


async def test_member_cannot_change_workspace_roles(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    target = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)

    response = await client.put(f"/api/users/{target.user_id}/workspace-role", json={"workspaceRole": "admin"})

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


async def test_owner_cannot_change_own_role_or_grant_ownership(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)

    self_response = await client.put(f"/api/users/{owner.user_id}/workspace-role", json={"workspaceRole": "member"})
    owner_value_response = await client.put(
        f"/api/users/{member.user_id}/workspace-role", json={"workspaceRole": "owner"}
    )
    unknown_response = await client.put(
        "/api/users/00000000-0000-7000-8000-000000000000/workspace-role", json={"workspaceRole": "admin"}
    )

    assert self_response.status_code == 409
    assert self_response.json()["code"] == "CANNOT_CHANGE_OWN_OR_OWNER"
    assert owner_value_response.status_code == 422
    assert unknown_response.status_code == 404

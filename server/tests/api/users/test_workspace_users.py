import uuid

from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import create_invited_user, sign_up_as, use_session
from tests.api.users.account_steps import read_invite_token
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import PASSWORD


def build_marker() -> str:
    return f"m{uuid.uuid4().hex[:10]}"


async def test_workspace_member_cannot_list_users(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)

    response = await client.get("/api/users")

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


async def test_admin_lists_users_with_filters(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    marker = build_marker()
    invited_user_id = await create_invited_user(container, recording_mailer, f"Bea {marker}")
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, f"Cid {marker}")
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN, f"alma {marker}")

    all_response = await client.get("/api/users", params={"query": marker})
    invited_response = await client.get("/api/users", params={"query": marker, "status": "invited"})
    admin_response = await client.get("/api/users", params={"query": marker, "workspaceRole": "admin"})
    email_response = await client.get("/api/users", params={"query": member.email.upper()})

    assert all_response.status_code == 200
    assert [user["id"] for user in all_response.json()] == [
        str(admin.user_id),
        str(invited_user_id),
        str(member.user_id),
    ]
    assert [user["id"] for user in invited_response.json()] == [str(invited_user_id)]
    assert [user["id"] for user in admin_response.json()] == [str(admin.user_id)]
    assert [user["id"] for user in email_response.json()] == [str(member.user_id)]
    first_user = all_response.json()[0]
    assert first_user["workspaceRole"] == "admin"
    assert first_user["status"] == "active"
    assert first_user["isTwoFactorSetUp"] is True
    assert first_user["avatarUrl"] is None
    assert first_user["deactivatedAt"] is None


async def test_user_query_treats_like_wildcards_as_text(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    response = await client.get("/api/users", params={"query": "%_%nobody-matches-this"})

    assert response.status_code == 200
    assert response.json() == []


async def test_admin_invites_a_member(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    email = f"new-{uuid.uuid4().hex[:8]}@tessio.test"

    response = await client.post("/api/users", json={"email": email, "name": "  Nora New  "})

    assert response.status_code == 201
    assert response.json()["email"] == email
    assert response.json()["name"] == "Nora New"
    assert response.json()["workspaceRole"] == "member"
    assert response.json()["status"] == "invited"
    assert recording_mailer.messages[-1].recipient == email
    assert "/invite/" in recording_mailer.messages[-1].text


async def test_admin_cannot_invite_an_admin(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    response = await client.post(
        "/api/users",
        json={"email": f"boss-{uuid.uuid4().hex[:8]}@tessio.test", "name": "Boss", "workspaceRole": "admin"},
    )

    assert response.status_code == 403
    assert response.json()["code"] == "OWNER_ONLY"


async def test_owner_invites_an_admin(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)

    response = await client.post(
        "/api/users",
        json={"email": f"boss-{uuid.uuid4().hex[:8]}@tessio.test", "name": "Boss", "workspaceRole": "admin"},
    )

    assert response.status_code == 201
    assert response.json()["workspaceRole"] == "admin"


async def test_invite_refuses_the_owner_role_and_bad_input(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    email = f"boss-{uuid.uuid4().hex[:8]}@tessio.test"

    owner_response = await client.post("/api/users", json={"email": email, "name": "Boss", "workspaceRole": "owner"})
    email_response = await client.post("/api/users", json={"email": "not-an-email", "name": "Boss"})
    name_response = await client.post("/api/users", json={"email": email, "name": "   "})

    assert owner_response.status_code == 422
    assert email_response.status_code == 422
    assert name_response.status_code == 422


async def test_invite_with_a_used_email_conflicts(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    response = await client.post("/api/users", json={"email": member.email, "name": "Again"})

    assert response.status_code == 409
    assert response.json()["code"] == "EMAIL_ALREADY_USED"


async def test_resend_invite_replaces_the_old_link(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    invited_user_id = await create_invited_user(container, recording_mailer)
    old_token = read_invite_token(recording_mailer)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    resend_response = await client.post(f"/api/users/{invited_user_id}/resend-invite")
    new_token = read_invite_token(recording_mailer)
    client.cookies.clear()
    old_link_response = await client.post(f"/api/auth/invites/{old_token}", json={"password": PASSWORD})
    new_link_response = await client.post(f"/api/auth/invites/{new_token}", json={"password": PASSWORD})

    assert resend_response.status_code == 204
    assert new_token != old_token
    assert old_link_response.status_code == 400
    assert old_link_response.json()["code"] == "INVALID_ONE_TIME_LINK"
    assert new_link_response.status_code == 200


async def test_resend_invite_to_an_active_user_conflicts(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    use_session(client, admin.session_token)

    response = await client.post(f"/api/users/{member.user_id}/resend-invite")

    assert response.status_code == 409
    assert response.json()["code"] == "USER_NOT_INVITED"


async def test_admin_gets_a_user_and_unknown_users_are_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, "Mia Member")
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    found_response = await client.get(f"/api/users/{member.user_id}")
    missing_response = await client.get("/api/users/00000000-0000-7000-8000-000000000000")

    assert found_response.status_code == 200
    assert found_response.json()["name"] == "Mia Member"
    assert found_response.json()["email"] == member.email
    assert missing_response.status_code == 404
    assert missing_response.json()["code"] == "NOT_FOUND"


async def test_users_endpoints_need_a_signed_in_session(client: AsyncClient) -> None:
    client.cookies.clear()

    response = await client.get("/api/users")

    assert response.status_code == 401
    assert response.json()["code"] == "NOT_SIGNED_IN"

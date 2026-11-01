import re

from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import create_invited_user, sign_up_as, use_session
from tests.api.users.account_steps import read_invite_token, sign_in_with_password
from tests.api.users.recording_api_token_revoker import RecordingApiTokenRevoker
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import PASSWORD


def install_revoker(container: Container) -> RecordingApiTokenRevoker:
    revoker = RecordingApiTokenRevoker()
    container.__dict__["api_token_revoker"] = revoker
    return revoker


async def test_deactivate_ends_sessions_links_and_tokens(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    revoker = install_revoker(container)
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await client.post("/api/auth/password/forgot", json={"email": member.email})
    reset_match = re.search(r"/reset-password/(\S+)", recording_mailer.messages[-1].text)
    assert reset_match is not None
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    use_session(client, admin.session_token)

    deactivate_response = await client.post(f"/api/users/{member.user_id}/deactivate")
    use_session(client, member.session_token)
    member_me_response = await client.get("/api/auth/me")
    sign_in_status = await sign_in_with_password(client, member.email)
    reset_response = await client.post(
        "/api/auth/password/reset", json={"token": reset_match.group(1), "password": "a brand new passphrase"}
    )

    assert deactivate_response.status_code == 200
    assert deactivate_response.json()["status"] == "deactivated"
    assert deactivate_response.json()["deactivatedAt"] is not None
    assert member_me_response.status_code == 401
    assert revoker.revoked_user_ids == [member.user_id]
    assert sign_in_status == 401
    assert reset_response.status_code == 400
    assert reset_response.json()["code"] == "INVALID_ONE_TIME_LINK"


async def test_deactivate_is_idempotent(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    revoker = install_revoker(container)
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    first_response = await client.post(f"/api/users/{member.user_id}/deactivate")
    second_response = await client.post(f"/api/users/{member.user_id}/deactivate")

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_response.json()["status"] == "deactivated"
    assert second_response.json()["deactivatedAt"] == first_response.json()["deactivatedAt"]
    assert revoker.revoked_user_ids == [member.user_id]


async def test_deactivate_refuses_self_owner_and_admins_for_admins(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    install_revoker(container)
    owner = await sign_up_as(client, container, recording_mailer, WorkspaceRole.OWNER)
    other_admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    self_response = await client.post(f"/api/users/{admin.user_id}/deactivate")
    owner_response = await client.post(f"/api/users/{owner.user_id}/deactivate")
    admin_response = await client.post(f"/api/users/{other_admin.user_id}/deactivate")
    use_session(client, owner.session_token)
    owner_on_admin_response = await client.post(f"/api/users/{other_admin.user_id}/deactivate")

    assert self_response.status_code == 409
    assert self_response.json()["code"] == "CANNOT_CHANGE_OWN_OR_OWNER"
    assert owner_response.status_code == 409
    assert owner_response.json()["code"] == "CANNOT_CHANGE_OWN_OR_OWNER"
    assert admin_response.status_code == 403
    assert admin_response.json()["code"] == "OWNER_ONLY"
    assert owner_on_admin_response.status_code == 200


async def test_member_and_unknown_targets_are_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    install_revoker(container)
    target = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)

    member_response = await client.post(f"/api/users/{target.user_id}/deactivate")
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    unknown_response = await client.post("/api/users/00000000-0000-7000-8000-000000000000/deactivate")

    assert member_response.status_code == 403
    assert member_response.json()["code"] == "PERMISSION_DENIED"
    assert unknown_response.status_code == 404
    assert unknown_response.json()["code"] == "NOT_FOUND"


async def test_deactivating_an_invited_user_cancels_the_invite(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    install_revoker(container)
    invited_user_id = await create_invited_user(container, recording_mailer)
    invite_token = read_invite_token(recording_mailer)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    deactivate_response = await client.post(f"/api/users/{invited_user_id}/deactivate")
    client.cookies.clear()
    accept_response = await client.post(f"/api/auth/invites/{invite_token}", json={"password": PASSWORD})

    assert deactivate_response.status_code == 200
    assert accept_response.status_code == 400
    assert accept_response.json()["code"] == "INVALID_ONE_TIME_LINK"


async def test_reactivate_restores_sign_in(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    install_revoker(container)
    member = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER)
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    await client.post(f"/api/users/{member.user_id}/deactivate")

    reactivate_response = await client.post(f"/api/users/{member.user_id}/reactivate")
    sign_in_response = await client.post("/api/auth/sign-in", json={"email": member.email, "password": PASSWORD})
    use_session(client, admin.session_token)
    repeat_response = await client.post(f"/api/users/{member.user_id}/reactivate")

    assert reactivate_response.status_code == 200
    assert reactivate_response.json()["status"] == "active"
    assert reactivate_response.json()["deactivatedAt"] is None
    assert reactivate_response.json()["isTwoFactorSetUp"] is True
    assert sign_in_response.status_code == 200
    assert sign_in_response.json() == {"nextStep": "two_factor_required"}
    assert repeat_response.status_code == 200
    assert repeat_response.json()["status"] == "active"


async def test_reactivate_reinvites_a_user_who_never_accepted(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    install_revoker(container)
    invited_user_id = await create_invited_user(container, recording_mailer)
    old_token = read_invite_token(recording_mailer)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    await client.post(f"/api/users/{invited_user_id}/deactivate")
    message_count = len(recording_mailer.messages)

    reactivate_response = await client.post(f"/api/users/{invited_user_id}/reactivate")
    new_token = read_invite_token(recording_mailer)
    client.cookies.clear()
    accept_response = await client.post(f"/api/auth/invites/{new_token}", json={"password": PASSWORD})

    assert reactivate_response.status_code == 200
    assert reactivate_response.json()["status"] == "invited"
    assert reactivate_response.json()["deactivatedAt"] is None
    assert len(recording_mailer.messages) == message_count + 1
    assert new_token != old_token
    assert accept_response.status_code == 200

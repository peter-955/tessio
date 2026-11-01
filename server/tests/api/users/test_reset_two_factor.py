import pyotp
from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import sign_up_as, use_session
from tests.api.users.account_steps import sign_in_with_password, sign_up_with_two_factor
from tests.conftest import RecordingMailer


async def test_admin_reset_clears_two_factor_sessions_and_recovery_codes(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    reset_response = await client.post(f"/api/users/{member.user_id}/reset-two-factor")
    use_session(client, member.session_token)
    old_session_response = await client.get("/api/auth/me")
    sign_in_status = await sign_in_with_password(client, member.email)
    me_response = await client.get("/api/auth/me")
    old_code_response = await client.post("/api/auth/two-factor", json={"code": member.recovery_codes[0]})
    use_session(client, admin.session_token)
    repeat_response = await client.post(f"/api/users/{member.user_id}/reset-two-factor")

    assert reset_response.status_code == 200
    assert reset_response.json()["isTwoFactorSetUp"] is False
    assert old_session_response.status_code == 401
    assert sign_in_status == 200
    assert me_response.json()["nextStep"] == "two_factor_setup_required"
    assert old_code_response.status_code == 409
    assert old_code_response.json()["code"] == "TWO_FACTOR_SETUP_NOT_STARTED"
    assert repeat_response.status_code == 200


async def test_old_recovery_codes_fail_after_setting_up_again(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    member = await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)
    await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)
    await client.post(f"/api/users/{member.user_id}/reset-two-factor")
    await sign_in_with_password(client, member.email)
    setup_response = await client.post("/api/auth/two-factor/setup")
    confirm_response = await client.post(
        "/api/auth/two-factor/confirm", json={"code": pyotp.TOTP(setup_response.json()["key"]).now()}
    )
    await sign_in_with_password(client, member.email)

    old_code_response = await client.post("/api/auth/two-factor", json={"code": member.recovery_codes[1]})
    new_code_response = await client.post(
        "/api/auth/two-factor", json={"code": confirm_response.json()["recoveryCodes"][0]}
    )

    assert confirm_response.status_code == 200
    assert old_code_response.status_code == 400
    assert old_code_response.json()["code"] == "INVALID_TWO_FACTOR_CODE"
    assert new_code_response.status_code == 200


async def test_admin_cannot_reset_own_two_factor_here(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    admin = await sign_up_as(client, container, recording_mailer, WorkspaceRole.ADMIN)

    response = await client.post(f"/api/users/{admin.user_id}/reset-two-factor")

    assert response.status_code == 409
    assert response.json()["code"] == "CANNOT_CHANGE_OWN_OR_OWNER"

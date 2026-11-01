import pyotp
from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import use_session
from tests.api.users.account_steps import (
    open_session_with_recovery_code,
    sign_in_with_password,
    sign_up_with_two_factor,
)
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import PASSWORD


async def test_regenerate_recovery_codes_replaces_the_old_ones(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account = await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)

    regenerate_response = await client.post("/api/me/recovery-codes", json={"password": PASSWORD})
    new_codes = regenerate_response.json()["recoveryCodes"]
    await sign_in_with_password(client, account.email)
    old_code_response = await client.post("/api/auth/two-factor", json={"code": account.recovery_codes[0]})
    new_code_response = await client.post("/api/auth/two-factor", json={"code": new_codes[0]})

    assert regenerate_response.status_code == 200
    assert len(new_codes) == 10
    assert set(new_codes).isdisjoint(account.recovery_codes)
    assert old_code_response.status_code == 400
    assert old_code_response.json()["code"] == "INVALID_TWO_FACTOR_CODE"
    assert new_code_response.status_code == 200


async def test_regenerate_recovery_codes_needs_the_password(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)

    response = await client.post("/api/me/recovery-codes", json={"password": "wrong password"})

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_CURRENT_PASSWORD"


async def test_reset_own_two_factor_starts_setup_again(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account = await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)
    other_session_token = await open_session_with_recovery_code(client, account.email, account.recovery_codes[0])
    use_session(client, account.session_token)

    reset_response = await client.post("/api/me/two-factor/reset", json={"password": PASSWORD})
    me_response = await client.get("/api/auth/me")
    setup_response = await client.post("/api/auth/two-factor/setup")
    confirm_response = await client.post(
        "/api/auth/two-factor/confirm", json={"code": pyotp.TOTP(setup_response.json()["key"]).now()}
    )
    signed_in_response = await client.get("/api/auth/me")
    use_session(client, other_session_token)
    other_session_response = await client.get("/api/auth/me")

    assert reset_response.status_code == 200
    assert reset_response.json() == {"nextStep": "two_factor_setup_required"}
    assert "tessio_session=" in reset_response.headers["set-cookie"]
    assert me_response.json()["nextStep"] == "two_factor_setup_required"
    assert me_response.json()["isTwoFactorSetUp"] is False
    assert setup_response.status_code == 200
    assert setup_response.json()["key"] != account.totp_key
    assert confirm_response.status_code == 200
    assert signed_in_response.json()["nextStep"] == "signed_in"
    assert other_session_response.status_code == 401


async def test_reset_own_two_factor_needs_the_password(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)

    response = await client.post("/api/me/two-factor/reset", json={"password": "wrong password"})
    me_response = await client.get("/api/auth/me")

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_CURRENT_PASSWORD"
    assert me_response.json()["nextStep"] == "signed_in"

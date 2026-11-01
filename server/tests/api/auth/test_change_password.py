from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import use_session
from tests.api.users.account_steps import (
    open_session_with_recovery_code,
    sign_in_with_password,
    sign_up_with_two_factor,
)
from tests.conftest import BREACHED_PASSWORD, RecordingMailer
from tests.support.sign_in_steps import PASSWORD

NEW_PASSWORD = "a brand new passphrase"


async def test_change_password_keeps_this_session_and_ends_the_others(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account = await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)
    other_session_token = await open_session_with_recovery_code(client, account.email, account.recovery_codes[0])
    use_session(client, account.session_token)

    change_response = await client.put(
        "/api/me/password", json={"currentPassword": PASSWORD, "newPassword": NEW_PASSWORD}
    )
    current_session_response = await client.get("/api/auth/me")
    use_session(client, other_session_token)
    other_session_response = await client.get("/api/auth/me")
    old_password_status = await sign_in_with_password(client, account.email, PASSWORD)
    new_password_status = await sign_in_with_password(client, account.email, NEW_PASSWORD)

    assert change_response.status_code == 204
    assert current_session_response.status_code == 200
    assert other_session_response.status_code == 401
    assert old_password_status == 401
    assert new_password_status == 200


async def test_change_password_checks_the_current_password_first(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)

    response = await client.put("/api/me/password", json={"currentPassword": "wrong password", "newPassword": "short"})

    assert response.status_code == 400
    assert response.json()["code"] == "INVALID_CURRENT_PASSWORD"


async def test_change_password_refuses_weak_and_breached_passwords(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)

    weak_response = await client.put("/api/me/password", json={"currentPassword": PASSWORD, "newPassword": "short"})
    breached_response = await client.put(
        "/api/me/password", json={"currentPassword": PASSWORD, "newPassword": BREACHED_PASSWORD}
    )

    assert weak_response.status_code == 422
    assert weak_response.json()["code"] == "WEAK_PASSWORD"
    assert breached_response.status_code == 422
    assert breached_response.json()["code"] == "PASSWORD_BREACHED"


async def test_wrong_current_passwords_do_not_lock_sign_in(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account = await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)
    for _ in range(6):
        await client.put("/api/me/password", json={"currentPassword": "wrong password", "newPassword": NEW_PASSWORD})

    sign_in_status = await sign_in_with_password(client, account.email)

    assert sign_in_status == 200

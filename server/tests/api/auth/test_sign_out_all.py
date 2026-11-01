from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import use_session
from tests.api.users.account_steps import open_session_with_recovery_code, sign_up_with_two_factor
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import PASSWORD


async def test_sign_out_all_ends_every_session_and_clears_the_cookie(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account = await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)
    other_session_token = await open_session_with_recovery_code(client, account.email, account.recovery_codes[0])
    use_session(client, account.session_token)

    sign_out_response = await client.post("/api/auth/sign-out-all")
    use_session(client, account.session_token)
    current_session_response = await client.get("/api/auth/me")
    use_session(client, other_session_token)
    other_session_response = await client.get("/api/auth/me")

    set_cookie = sign_out_response.headers["set-cookie"].lower()
    assert sign_out_response.status_code == 204
    assert "tessio_session=" in set_cookie
    assert "max-age=0" in set_cookie
    assert current_session_response.status_code == 401
    assert other_session_response.status_code == 401


async def test_sign_out_all_needs_a_full_session(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    account = await sign_up_with_two_factor(client, container, recording_mailer, WorkspaceRole.MEMBER)
    client.cookies.clear()
    await client.post("/api/auth/sign-in", json={"email": account.email, "password": PASSWORD})

    response = await client.post("/api/auth/sign-out-all")

    assert response.status_code == 401
    assert response.json()["code"] == "NOT_SIGNED_IN"

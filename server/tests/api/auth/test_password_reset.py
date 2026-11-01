import re

from httpx import AsyncClient

from app.container import Container
from tests.conftest import BREACHED_PASSWORD, RecordingMailer
from tests.support.sign_in_steps import PASSWORD, sign_up

NEW_PASSWORD = "a brand new passphrase"


async def request_reset_token(client: AsyncClient, recording_mailer: RecordingMailer, email: str) -> str:
    response = await client.post("/api/auth/password/forgot", json={"email": email})
    assert response.status_code == 204
    reset_match = re.search(r"/reset-password/(\S+)", recording_mailer.messages[-1].text)
    assert reset_match is not None
    return reset_match.group(1)


async def test_forgot_password_emails_a_reset_link(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)

    await request_reset_token(client, recording_mailer, signed_up_user.email)

    assert recording_mailer.messages[-1].recipient == signed_up_user.email
    assert "30 minutes" in recording_mailer.messages[-1].text


async def test_forgot_password_for_an_unknown_email_sends_nothing(
    client: AsyncClient, recording_mailer: RecordingMailer
) -> None:
    response = await client.post("/api/auth/password/forgot", json={"email": "nobody@tessio.test"})

    assert response.status_code == 204
    assert recording_mailer.messages == []


async def test_reset_signs_out_everywhere_and_still_requires_two_factor(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    old_session_cookie = client.cookies["tessio_session"]
    reset_token = await request_reset_token(client, recording_mailer, signed_up_user.email)

    reset_response = await client.post(
        "/api/auth/password/reset", json={"token": reset_token, "password": NEW_PASSWORD}
    )
    client.cookies.set("tessio_session", old_session_cookie)
    old_session_response = await client.get("/api/auth/me")
    old_password_response = await client.post(
        "/api/auth/sign-in", json={"email": signed_up_user.email, "password": PASSWORD}
    )
    new_password_response = await client.post(
        "/api/auth/sign-in", json={"email": signed_up_user.email, "password": NEW_PASSWORD}
    )

    assert reset_response.status_code == 204
    assert old_session_response.status_code == 401
    assert old_password_response.status_code == 401
    assert new_password_response.json() == {"nextStep": "two_factor_required"}


async def test_reset_link_works_only_once(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    reset_token = await request_reset_token(client, recording_mailer, signed_up_user.email)
    await client.post("/api/auth/password/reset", json={"token": reset_token, "password": NEW_PASSWORD})

    second_response = await client.post(
        "/api/auth/password/reset", json={"token": reset_token, "password": "yet another passphrase"}
    )

    assert second_response.status_code == 400
    assert second_response.json()["code"] == "INVALID_ONE_TIME_LINK"


async def test_reset_refuses_a_breached_password(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    reset_token = await request_reset_token(client, recording_mailer, signed_up_user.email)

    response = await client.post("/api/auth/password/reset", json={"token": reset_token, "password": BREACHED_PASSWORD})

    assert response.status_code == 422
    assert response.json()["code"] == "PASSWORD_BREACHED"


async def test_reset_unlocks_a_locked_account(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    await client.post("/api/auth/sign-out")
    for _ in range(5):
        await client.post("/api/auth/sign-in", json={"email": signed_up_user.email, "password": "not the right one"})
    reset_token = await request_reset_token(client, recording_mailer, signed_up_user.email)
    await client.post("/api/auth/password/reset", json={"token": reset_token, "password": NEW_PASSWORD})

    response = await client.post("/api/auth/sign-in", json={"email": signed_up_user.email, "password": NEW_PASSWORD})

    assert response.status_code == 200

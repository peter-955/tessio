from httpx import AsyncClient

from app.container import Container
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import PASSWORD, generate_next_totp_code, invite_user, sign_up


async def test_invited_user_reaches_the_app_after_password_and_two_factor(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)

    me_response = await client.get("/api/auth/me")

    assert me_response.status_code == 200
    assert me_response.json()["email"] == signed_up_user.email
    assert me_response.json()["workspaceRole"] == "owner"
    assert me_response.json()["nextStep"] == "signed_in"
    assert len(signed_up_user.recovery_codes) == 10


async def test_invite_email_is_sent_to_the_invited_address(
    container: Container, recording_mailer: RecordingMailer
) -> None:
    email, _ = await invite_user(container, recording_mailer)

    assert recording_mailer.messages[-1].recipient == email
    assert "https://tessio.test/invite/" in recording_mailer.messages[-1].text


async def test_app_is_refused_until_two_factor_is_set_up(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, invite_token = await invite_user(container, recording_mailer)
    await client.post(f"/api/auth/invites/{invite_token}", json={"password": PASSWORD})

    me_response = await client.get("/api/auth/me")
    events_response = await client.get("/api/events")

    assert me_response.status_code == 200
    assert me_response.json()["nextStep"] == "two_factor_setup_required"
    assert events_response.status_code == 401
    assert events_response.json()["code"] == "NOT_SIGNED_IN"


async def test_session_cookie_is_http_only_secure_and_lax(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, invite_token = await invite_user(container, recording_mailer)

    accept_response = await client.post(f"/api/auth/invites/{invite_token}", json={"password": PASSWORD})

    set_cookie = accept_response.headers["set-cookie"].lower()
    assert "tessio_session=" in set_cookie
    assert "httponly" in set_cookie
    assert "secure" in set_cookie
    assert "samesite=lax" in set_cookie


async def test_invite_link_works_only_once(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, invite_token = await invite_user(container, recording_mailer)
    await client.post(f"/api/auth/invites/{invite_token}", json={"password": PASSWORD})

    second_response = await client.post(f"/api/auth/invites/{invite_token}", json={"password": PASSWORD})

    assert second_response.status_code == 400
    assert second_response.json()["code"] == "INVALID_ONE_TIME_LINK"


async def test_short_password_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, invite_token = await invite_user(container, recording_mailer)

    response = await client.post(f"/api/auth/invites/{invite_token}", json={"password": "too-short"})

    assert response.status_code == 422
    assert response.json()["code"] == "WEAK_PASSWORD"


async def test_sign_in_asks_for_two_factor_then_accepts_a_totp_code(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    await client.post("/api/auth/sign-out")

    sign_in_response = await client.post(
        "/api/auth/sign-in", json={"email": signed_up_user.email.upper(), "password": PASSWORD}
    )
    half_session_response = await client.get("/api/auth/me")
    blocked_response = await client.get("/api/events")
    verify_response = await client.post(
        "/api/auth/two-factor", json={"code": generate_next_totp_code(signed_up_user.totp_key)}
    )
    me_response = await client.get("/api/auth/me")

    assert sign_in_response.json() == {"nextStep": "two_factor_required"}
    assert half_session_response.json()["nextStep"] == "two_factor_required"
    assert blocked_response.status_code == 401
    assert verify_response.json() == {"nextStep": "signed_in"}
    assert me_response.status_code == 200


async def test_totp_code_cannot_be_used_twice(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    code = generate_next_totp_code(signed_up_user.totp_key)
    await client.post("/api/auth/sign-out")
    await client.post("/api/auth/sign-in", json={"email": signed_up_user.email, "password": PASSWORD})
    await client.post("/api/auth/two-factor", json={"code": code})
    await client.post("/api/auth/sign-out")
    await client.post("/api/auth/sign-in", json={"email": signed_up_user.email, "password": PASSWORD})

    replay_response = await client.post("/api/auth/two-factor", json={"code": code})

    assert replay_response.status_code == 400
    assert replay_response.json()["code"] == "INVALID_TWO_FACTOR_CODE"


async def test_recovery_code_signs_in_only_once(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    recovery_code = signed_up_user.recovery_codes[0]
    await client.post("/api/auth/sign-out")
    await client.post("/api/auth/sign-in", json={"email": signed_up_user.email, "password": PASSWORD})

    first_response = await client.post("/api/auth/two-factor", json={"code": recovery_code.upper()})
    await client.post("/api/auth/sign-out")
    await client.post("/api/auth/sign-in", json={"email": signed_up_user.email, "password": PASSWORD})
    second_response = await client.post("/api/auth/two-factor", json={"code": recovery_code})

    assert first_response.json() == {"nextStep": "signed_in"}
    assert second_response.status_code == 400


async def test_wrong_password_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    await client.post("/api/auth/sign-out")

    response = await client.post(
        "/api/auth/sign-in", json={"email": signed_up_user.email, "password": "not the right password"}
    )

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


async def test_unknown_email_gets_the_same_answer_as_a_wrong_password(client: AsyncClient) -> None:
    response = await client.post("/api/auth/sign-in", json={"email": "nobody@tessio.test", "password": PASSWORD})

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_CREDENTIALS"


async def test_sign_out_ends_the_session(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await sign_up(client, container, recording_mailer)
    old_cookie = client.cookies["tessio_session"]

    await client.post("/api/auth/sign-out")
    client.cookies.set("tessio_session", old_cookie)
    me_response = await client.get("/api/auth/me")

    assert me_response.status_code == 401


async def test_session_token_changes_after_two_factor(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    await client.post("/api/auth/sign-out")
    await client.post("/api/auth/sign-in", json={"email": signed_up_user.email, "password": PASSWORD})
    half_session_cookie = client.cookies["tessio_session"]

    await client.post("/api/auth/two-factor", json={"code": generate_next_totp_code(signed_up_user.totp_key)})
    client.cookies.set("tessio_session", half_session_cookie)
    me_response = await client.get("/api/auth/me")

    assert me_response.status_code == 401

import pyotp
from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import invite_with_role
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import PASSWORD, sign_up

UNKNOWN_EMAIL = "nobody@tessio.test"


async def test_the_twenty_first_sign_in_from_one_address_is_refused(client: AsyncClient) -> None:
    allowed_responses = [
        await client.post("/api/auth/sign-in", json={"email": UNKNOWN_EMAIL, "password": PASSWORD}) for _ in range(20)
    ]

    refused_response = await client.post("/api/auth/sign-in", json={"email": UNKNOWN_EMAIL, "password": PASSWORD})

    assert {response.status_code for response in allowed_responses} == {401}
    assert refused_response.status_code == 429
    assert refused_response.json() == {"code": "RATE_LIMITED", "message": "Too many attempts. Try again later."}
    assert int(refused_response.headers["retry-after"]) == 15 * 60


async def test_a_refused_sign_in_is_refused_before_its_body_is_read(client: AsyncClient) -> None:
    for _ in range(20):
        await client.post("/api/auth/sign-in", json={"email": UNKNOWN_EMAIL, "password": PASSWORD})

    refused_response = await client.post("/api/auth/sign-in", json={})

    assert refused_response.status_code == 429


async def test_forgot_password_stops_emailing_after_three_requests_for_one_email(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    recording_mailer.messages.clear()

    responses = [await client.post("/api/auth/password/forgot", json={"email": signed_up_user.email}) for _ in range(4)]

    assert [response.status_code for response in responses] == [204, 204, 204, 204]
    assert len(recording_mailer.messages) == 3
    assert {message.recipient for message in recording_mailer.messages} == {signed_up_user.email}


async def test_the_per_email_limit_ignores_case_and_spaces(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    recording_mailer.messages.clear()

    for email in (signed_up_user.email, signed_up_user.email.upper(), f" {signed_up_user.email} "):
        await client.post("/api/auth/password/forgot", json={"email": email})
    fourth_response = await client.post("/api/auth/password/forgot", json={"email": signed_up_user.email})

    assert fourth_response.status_code == 204
    assert len(recording_mailer.messages) == 3


async def test_the_eleventh_forgot_password_from_one_address_is_refused(client: AsyncClient) -> None:
    allowed_responses = [
        await client.post("/api/auth/password/forgot", json={"email": f"user-{index}@tessio.test"})
        for index in range(10)
    ]

    refused_response = await client.post("/api/auth/password/forgot", json={"email": UNKNOWN_EMAIL})

    assert {response.status_code for response in allowed_responses} == {204}
    assert refused_response.status_code == 429
    assert refused_response.json()["code"] == "RATE_LIMITED"


async def test_the_twenty_first_one_time_link_attempt_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, _, invite_token = await invite_with_role(container, recording_mailer, WorkspaceRole.MEMBER, "Ivy Invited")
    for _ in range(10):
        await client.post("/api/auth/invites/not-a-token", json={"password": PASSWORD})
        await client.post("/api/auth/password/reset", json={"token": "not-a-token", "password": PASSWORD})

    refused_response = await client.post(f"/api/auth/invites/{invite_token}", json={"password": PASSWORD})

    assert refused_response.status_code == 429
    assert refused_response.json()["code"] == "RATE_LIMITED"


async def test_the_twenty_first_two_factor_attempt_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, _, invite_token = await invite_with_role(container, recording_mailer, WorkspaceRole.MEMBER, "Tess Two")
    await client.post(f"/api/auth/invites/{invite_token}", json={"password": PASSWORD})
    setup_response = await client.post("/api/auth/two-factor/setup")
    totp_key = setup_response.json()["key"]
    for _ in range(20):
        await client.post("/api/auth/two-factor/confirm", json={"code": "000000"})

    refused_response = await client.post("/api/auth/two-factor/confirm", json={"code": pyotp.TOTP(totp_key).now()})

    assert refused_response.status_code == 429
    assert refused_response.json()["code"] == "RATE_LIMITED"

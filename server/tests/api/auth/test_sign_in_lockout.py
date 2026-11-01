from httpx import AsyncClient

from app.container import Container
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import PASSWORD, generate_next_totp_code, sign_up

WRONG_PASSWORD = "not the right password"


async def sign_in(client: AsyncClient, email: str, password: str) -> int:
    response = await client.post("/api/auth/sign-in", json={"email": email, "password": password})
    return response.status_code


async def test_five_wrong_passwords_lock_the_account(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    await client.post("/api/auth/sign-out")

    wrong_statuses = [await sign_in(client, signed_up_user.email, WRONG_PASSWORD) for _ in range(5)]
    locked_response = await client.post("/api/auth/sign-in", json={"email": signed_up_user.email, "password": PASSWORD})

    assert wrong_statuses == [401] * 5
    assert locked_response.status_code == 429
    assert locked_response.json()["code"] == "SIGN_IN_LOCKED"


async def test_full_sign_in_resets_the_failed_count(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    await client.post("/api/auth/sign-out")
    for _ in range(4):
        await sign_in(client, signed_up_user.email, WRONG_PASSWORD)
    await sign_in(client, signed_up_user.email, PASSWORD)
    await client.post("/api/auth/two-factor", json={"code": generate_next_totp_code(signed_up_user.totp_key)})
    await client.post("/api/auth/sign-out")
    for _ in range(4):
        await sign_in(client, signed_up_user.email, WRONG_PASSWORD)

    status = await sign_in(client, signed_up_user.email, PASSWORD)

    assert status == 200


async def test_five_wrong_two_factor_codes_lock_and_end_the_half_session(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    signed_up_user = await sign_up(client, container, recording_mailer)
    await client.post("/api/auth/sign-out")
    await sign_in(client, signed_up_user.email, PASSWORD)

    wrong_statuses = [
        (await client.post("/api/auth/two-factor", json={"code": "000000"})).status_code for _ in range(5)
    ]
    after_lock_response = await client.post("/api/auth/two-factor", json={"code": "000000"})
    sign_in_status = await sign_in(client, signed_up_user.email, PASSWORD)

    assert wrong_statuses == [400] * 5
    assert after_lock_response.json()["code"] == "NOT_SIGNED_IN"
    assert sign_in_status == 429

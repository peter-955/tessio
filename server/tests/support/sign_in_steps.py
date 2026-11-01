import re
import time
import uuid
from dataclasses import dataclass

import pyotp
from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from tests.conftest import RecordingMailer

PASSWORD = "correct horse battery staple"


@dataclass(frozen=True)
class SignedUpUser:
    email: str
    totp_key: str
    recovery_codes: list[str]


async def invite_user(container: Container, recording_mailer: RecordingMailer) -> tuple[str, str]:
    email = f"owner-{uuid.uuid4().hex[:8]}@tessio.test"
    await container.invite_user.execute(email, "Olivia Owner", WorkspaceRole.OWNER)
    invite_match = re.search(r"/invite/(\S+)", recording_mailer.messages[-1].text)
    assert invite_match is not None
    return email, invite_match.group(1)


async def sign_up(client: AsyncClient, container: Container, recording_mailer: RecordingMailer) -> SignedUpUser:
    email, invite_token = await invite_user(container, recording_mailer)
    accept_response = await client.post(f"/api/auth/invites/{invite_token}", json={"password": PASSWORD})
    assert accept_response.json() == {"nextStep": "two_factor_setup_required"}
    setup_response = await client.post("/api/auth/two-factor/setup")
    totp_key = setup_response.json()["key"]
    confirm_response = await client.post("/api/auth/two-factor/confirm", json={"code": pyotp.TOTP(totp_key).now()})
    assert confirm_response.status_code == 200
    return SignedUpUser(email=email, totp_key=totp_key, recovery_codes=confirm_response.json()["recoveryCodes"])


def generate_next_totp_code(totp_key: str) -> str:
    return pyotp.TOTP(totp_key).at(int(time.time()) + 30)

import re
from dataclasses import dataclass
from datetime import UTC, datetime
from uuid import UUID, uuid7

import pyotp
from httpx import AsyncClient

from app.container import Container
from app.modules.files.domains.stored_file.entity import StoredFile
from app.modules.files.typing.enums import StoredFileKind, StoredFileStatus
from app.modules.users import WorkspaceRole
from tests.api.projects.user_steps import SESSION_COOKIE_NAME, invite_with_role
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import PASSWORD


@dataclass(frozen=True)
class TwoFactorAccount:
    user_id: UUID
    email: str
    session_token: str
    totp_key: str
    recovery_codes: list[str]


async def sign_up_with_two_factor(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    workspace_role: WorkspaceRole,
    name: str = "Test User",
) -> TwoFactorAccount:
    user_id, email, invite_token = await invite_with_role(container, recording_mailer, workspace_role, name)
    client.cookies.clear()
    accept_response = await client.post(f"/api/auth/invites/{invite_token}", json={"password": PASSWORD})
    assert accept_response.status_code == 200
    setup_response = await client.post("/api/auth/two-factor/setup")
    totp_key = setup_response.json()["key"]
    confirm_response = await client.post("/api/auth/two-factor/confirm", json={"code": pyotp.TOTP(totp_key).now()})
    assert confirm_response.status_code == 200
    return TwoFactorAccount(
        user_id=user_id,
        email=email,
        session_token=client.cookies[SESSION_COOKIE_NAME],
        totp_key=totp_key,
        recovery_codes=confirm_response.json()["recoveryCodes"],
    )


async def sign_in_with_password(client: AsyncClient, email: str, password: str = PASSWORD) -> int:
    client.cookies.clear()
    response = await client.post("/api/auth/sign-in", json={"email": email, "password": password})
    return response.status_code


async def open_session_with_recovery_code(client: AsyncClient, email: str, recovery_code: str) -> str:
    assert await sign_in_with_password(client, email) == 200
    verify_response = await client.post("/api/auth/two-factor", json={"code": recovery_code})
    assert verify_response.status_code == 200
    return client.cookies[SESSION_COOKIE_NAME]


def read_invite_token(recording_mailer: RecordingMailer) -> str:
    invite_match = re.search(r"/invite/(\S+)", recording_mailer.messages[-1].text)
    assert invite_match is not None
    return invite_match.group(1)


async def save_stored_file(
    container: Container,
    uploaded_by: UUID,
    status: StoredFileStatus = StoredFileStatus.UPLOADED,
    kind: StoredFileKind = StoredFileKind.AVATAR,
) -> StoredFile:
    file_id = uuid7()
    stored_file = StoredFile(
        id=file_id,
        project_id=None,
        kind=kind,
        object_key=f"avatars/{uploaded_by}/{file_id}/face.png",
        file_name="face.png",
        content_type="image/png",
        size=1024,
        sha256=None,
        status=status,
        uploaded_by=uploaded_by,
        created_at=datetime.now(UTC),
    )
    async with container.database.begin():
        await container.stored_file_repository.save(stored_file)
    return stored_file

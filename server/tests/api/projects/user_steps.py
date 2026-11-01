import re
import uuid
from dataclasses import dataclass
from uuid import UUID

import pyotp
from httpx import AsyncClient

from app.container import Container
from app.modules.users import UserStatus, WorkspaceRole
from tests.conftest import RecordingMailer
from tests.support.sign_in_steps import PASSWORD

SESSION_COOKIE_NAME = "tessio_session"


@dataclass(frozen=True)
class SignedUpAccount:
    user_id: UUID
    email: str
    session_token: str


async def invite_with_role(
    container: Container, recording_mailer: RecordingMailer, workspace_role: WorkspaceRole, name: str
) -> tuple[UUID, str, str]:
    email = f"{workspace_role.value}-{uuid.uuid4().hex[:8]}@tessio.test"
    user = await container.invite_user.execute(email, name, workspace_role)
    invite_match = re.search(r"/invite/(\S+)", recording_mailer.messages[-1].text)
    assert invite_match is not None
    return user.id, user.email, invite_match.group(1)


async def sign_up_as(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    workspace_role: WorkspaceRole,
    name: str = "Test User",
) -> SignedUpAccount:
    user_id, email, invite_token = await invite_with_role(container, recording_mailer, workspace_role, name)
    client.cookies.clear()
    accept_response = await client.post(f"/api/auth/invites/{invite_token}", json={"password": PASSWORD})
    assert accept_response.status_code == 200
    setup_response = await client.post("/api/auth/two-factor/setup")
    totp_key = setup_response.json()["key"]
    confirm_response = await client.post("/api/auth/two-factor/confirm", json={"code": pyotp.TOTP(totp_key).now()})
    assert confirm_response.status_code == 200
    return SignedUpAccount(user_id=user_id, email=email, session_token=client.cookies[SESSION_COOKIE_NAME])


def use_session(client: AsyncClient, session_token: str) -> None:
    client.cookies.clear()
    client.cookies.set(SESSION_COOKIE_NAME, session_token)


async def create_invited_user(
    container: Container, recording_mailer: RecordingMailer, name: str = "Ivy Invited"
) -> UUID:
    user_id, _, _ = await invite_with_role(container, recording_mailer, WorkspaceRole.MEMBER, name)
    return user_id


async def deactivate_user(container: Container, user_id: UUID) -> None:
    async with container.database.begin():
        user = await container.user_repository.find_by_id(user_id)
        assert user is not None
        await container.user_repository.update(user, user.model_copy(update={"status": UserStatus.DEACTIVATED}))


def generate_project_key() -> str:
    return "P" + uuid.uuid4().hex[:6].upper()


def build_create_project_body(key: str | None = None, jira_project_key: str | None = None) -> dict[str, str | int]:
    project_key = key or generate_project_key()
    return {
        "key": project_key,
        "name": f"Project {project_key}",
        "description": "Checkout flows",
        "jiraProjectKey": jira_project_key or f"J{project_key}",
        "jiraBoardId": 7,
    }

from collections.abc import Mapping

from httpx import AsyncClient, Response

from app.container import Container
from app.modules.integrations.domains.webhook_send_result.entity import WebhookSendResult
from app.modules.integrations.ports.webhook_sender import WebhookSender
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import sign_up_account
from tests.api.projects.user_steps import use_session
from tests.api.test_data.project_steps import SeededProject
from tests.conftest import RecordingMailer

WEBHOOK_URL = "https://hooks.example.com/tessio"


class RecordingWebhookSender(WebhookSender):
    def __init__(self) -> None:
        self.requests: list[tuple[str, bytes, dict[str, str]]] = []
        self.result = WebhookSendResult(is_success=True, response_status=200, error=None)

    async def send(self, url: str, body: bytes, headers: Mapping[str, str]) -> WebhookSendResult:
        self.requests.append((url, body, dict(headers)))
        return self.result


def use_recording_webhook_sender(container: Container) -> RecordingWebhookSender:
    sender = RecordingWebhookSender()
    container.__dict__["webhook_sender"] = sender
    return sender


def webhooks_path(project_key: str) -> str:
    return f"/api/projects/{project_key}/webhooks"


async def sign_in_project_admin(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, project: SeededProject
) -> None:
    admin = await sign_up_account(client, container, recording_mailer, project, ProjectRole.ADMIN)
    use_session(client, admin.session_token)


async def create_webhook(client: AsyncClient, project_key: str, **overrides: object) -> Response:
    body: dict[str, object] = {"url": WEBHOOK_URL, "events": ["run.finished"], **overrides}
    return await client.post(webhooks_path(project_key), json=body)


async def create_webhook_with_secret(client: AsyncClient, project_key: str, **overrides: object) -> tuple[str, str]:
    response = await create_webhook(client, project_key, **overrides)
    assert response.status_code == 201, response.text
    webhook_id: str = response.json()["webhook"]["id"]
    secret: str = response.json()["secret"]
    return webhook_id, secret

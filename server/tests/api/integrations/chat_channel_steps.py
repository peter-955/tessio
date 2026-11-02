from uuid import UUID

from httpx import AsyncClient, Response
from pydantic import JsonValue
from sqlalchemy import select

from app.container import Container
from app.modules.integrations.errors import ChatWebhookRejectedError
from app.modules.integrations.infrastructure import ProjectChatChannelTable
from app.modules.integrations.ports.chat_webhook_sender import ChatWebhookSender

SLACK_WEBHOOK_URL = "https://hooks.slack.com/services/T0001/B0002/SlackSecret1234"
TEAMS_WEBHOOK_URL = (
    "https://prod-01.westeurope.logic.azure.com:443/workflows/0a1b/triggers/manual/paths/invoke"
    "?api-version=2016-06-01&sig=TeamsSecret5678"
)


class RecordingChatWebhookSender(ChatWebhookSender):
    def __init__(self) -> None:
        self.deliveries: list[tuple[str, dict[str, JsonValue]]] = []
        self.failure: ChatWebhookRejectedError | None = None

    async def send(self, webhook_url: str, payload: dict[str, JsonValue]) -> None:
        self.deliveries.append((webhook_url, payload))
        if self.failure is not None:
            raise self.failure


def use_recording_sender(container: Container) -> RecordingChatWebhookSender:
    sender = RecordingChatWebhookSender()
    container.__dict__["chat_webhook_sender"] = sender
    return sender


def chat_channels_path(project_key: str) -> str:
    return f"/api/projects/{project_key}/chat-channels"


def build_channel_body(**overrides: object) -> dict[str, object]:
    return {
        "kind": "slack",
        "name": "QA alerts",
        "webhookUrl": SLACK_WEBHOOK_URL,
        "events": ["run.finished", "failure.opened"],
        **overrides,
    }


async def create_channel(client: AsyncClient, project_key: str, **overrides: object) -> Response:
    return await client.post(chat_channels_path(project_key), json=build_channel_body(**overrides))


async def create_channel_id(client: AsyncClient, project_key: str, **overrides: object) -> str:
    response = await create_channel(client, project_key, **overrides)
    assert response.status_code == 201, response.text
    chat_channel_id = response.json()["id"]
    assert isinstance(chat_channel_id, str)
    return chat_channel_id


async def find_channel_row(container: Container, chat_channel_id: str) -> ProjectChatChannelTable:
    async with container.database.begin():
        row = await container.database.get_current_session().scalar(
            select(ProjectChatChannelTable)
            .where(ProjectChatChannelTable.id == UUID(chat_channel_id))
            .execution_options(populate_existing=True)
        )
    assert row is not None
    return row

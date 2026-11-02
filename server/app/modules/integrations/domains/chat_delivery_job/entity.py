from uuid import UUID

from pydantic import Field

from app.modules.integrations.typing.enums import IntegrationEvent
from app.shared.common import Entity


class ChatDeliveryJob(Entity):
    chat_channel_id: UUID
    project_id: UUID
    event: IntegrationEvent
    ids: dict[str, str] = Field(default_factory=dict)

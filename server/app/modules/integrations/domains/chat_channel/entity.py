from datetime import datetime
from uuid import UUID

from app.modules.integrations.typing.enums import ChatChannelKind, ChatDeliveryStatus, IntegrationEvent
from app.shared.common import Entity


class ChatChannel(Entity):
    id: UUID
    project_id: UUID
    kind: ChatChannelKind
    name: str
    webhook_url_encrypted: bytes
    webhook_url_hint: str
    events: list[IntegrationEvent]
    is_active: bool
    last_delivery_status: ChatDeliveryStatus | None
    last_delivery_at: datetime | None
    last_delivery_error: str | None
    created_by: UUID
    created_at: datetime

    def is_subscribed_to(self, event: IntegrationEvent) -> bool:
        return self.is_active and event in self.events

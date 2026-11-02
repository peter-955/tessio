from datetime import datetime
from uuid import UUID

from app.modules.integrations.typing.enums import ChatChannelKind, ChatDeliveryStatus, IntegrationEvent
from app.shared.common import WireModel


class ChatChannelResponse(WireModel):
    id: UUID
    kind: ChatChannelKind
    name: str
    webhook_url_masked: str
    events: list[IntegrationEvent]
    is_active: bool
    last_delivery_status: ChatDeliveryStatus | None
    last_delivery_at: datetime | None
    last_delivery_error: str | None
    created_at: datetime

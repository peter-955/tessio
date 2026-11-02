from datetime import datetime
from uuid import UUID

from app.modules.integrations.models.webhook_delivery_response import WebhookDeliveryResponse
from app.modules.integrations.typing.enums.integration_event import IntegrationEvent
from app.shared.common import WireModel


class WebhookResponse(WireModel):
    id: UUID
    url: str
    description: str | None
    events: list[IntegrationEvent]
    is_active: bool
    secret_hint: str
    created_at: datetime
    last_delivery: WebhookDeliveryResponse | None

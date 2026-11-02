from datetime import datetime
from uuid import UUID

from pydantic import JsonValue

from app.modules.integrations.typing.enums.integration_event import IntegrationEvent
from app.modules.integrations.typing.enums.webhook import WebhookDeliveryStatus
from app.shared.common import WireModel


class WebhookDeliveryResponse(WireModel):
    id: UUID
    webhook_id: UUID
    event: IntegrationEvent
    status: WebhookDeliveryStatus
    attempts: int
    response_status: int | None
    error: str | None
    redelivery_of_id: UUID | None
    last_attempt_at: datetime | None
    delivered_at: datetime | None
    created_at: datetime
    payload: dict[str, JsonValue]

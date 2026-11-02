import json
from datetime import datetime
from uuid import UUID

from pydantic import JsonValue

from app.modules.integrations.domains.webhook_delivery.entity import WebhookDelivery
from app.modules.integrations.typing.constants.webhook import (
    WEBHOOK_DELIVERY_HEADER,
    WEBHOOK_EVENT_HEADER,
    WEBHOOK_SIGNATURE_HEADER,
    WEBHOOK_TIMESTAMP_HEADER,
    WEBHOOK_USER_AGENT,
)
from app.modules.integrations.typing.enums.integration_event import IntegrationEvent
from app.modules.integrations.utils.webhook_signature import sign_webhook_body
from app.modules.projects.domains.project.entity import Project


def build_webhook_payload(
    event_id: UUID, event: IntegrationEvent, project: Project, ids: dict[str, str], occurred_at: datetime
) -> dict[str, JsonValue]:
    data: dict[str, JsonValue] = dict(ids)
    return {
        "id": str(event_id),
        "event": event.value,
        "occurredAt": occurred_at.isoformat(),
        "project": {"id": str(project.id), "key": project.key, "name": project.name},
        "data": data,
    }


def serialize_webhook_payload(payload: dict[str, JsonValue]) -> bytes:
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":")).encode()


def build_webhook_headers(delivery: WebhookDelivery, secret: str, body: bytes, timestamp: int) -> dict[str, str]:
    return {
        "Content-Type": "application/json",
        "User-Agent": WEBHOOK_USER_AGENT,
        WEBHOOK_EVENT_HEADER: delivery.event.value,
        WEBHOOK_DELIVERY_HEADER: str(delivery.id),
        WEBHOOK_TIMESTAMP_HEADER: str(timestamp),
        WEBHOOK_SIGNATURE_HEADER: sign_webhook_body(secret, timestamp, body),
    }

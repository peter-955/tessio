from uuid import UUID

from app.shared.events import LiveEvent, LiveEventType


def build_webhook_changed_event(project_id: UUID, webhook_id: UUID) -> LiveEvent:
    return LiveEvent(type=LiveEventType.WEBHOOK_CHANGED, project_id=project_id, ids={"webhookId": str(webhook_id)})

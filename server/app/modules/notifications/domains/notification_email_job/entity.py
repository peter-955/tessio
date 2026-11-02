from uuid import UUID

from app.modules.notifications.domains.notification_payload.entity import NotificationPayload
from app.shared.common import Entity


class NotificationEmailJob(Entity):
    user_id: UUID
    project_id: UUID
    actor_id: UUID | None
    payload: NotificationPayload

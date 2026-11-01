from uuid import UUID

from app.modules.notifications.models.notification_response import NotificationResponse
from app.shared.common import WireModel


class NotificationPageResponse(WireModel):
    items: list[NotificationResponse]
    next_cursor: UUID | None

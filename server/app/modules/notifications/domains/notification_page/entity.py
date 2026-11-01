from uuid import UUID

from app.modules.notifications.domains.notification_list_item.entity import NotificationListItem
from app.shared.common import Entity


class NotificationPage(Entity):
    items: list[NotificationListItem]
    next_cursor: UUID | None

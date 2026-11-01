from app.modules.notifications.domains.notification.entity import Notification
from app.shared.common import Entity


class NotificationListItem(Entity):
    notification: Notification
    project_key: str
    project_name: str
    actor_name: str | None

from uuid import UUID

from app.modules.notifications.typing.enums import NotificationChannel, NotificationKind
from app.shared.common import Entity


class NotificationPreference(Entity):
    user_id: UUID
    kind: NotificationKind
    channel: NotificationChannel
    is_enabled: bool

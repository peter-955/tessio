from datetime import datetime
from uuid import UUID

from app.modules.notifications.domains.notification_payload.entity import NotificationPayload
from app.modules.notifications.typing.enums import NotificationKind
from app.shared.common import Entity


class Notification(Entity):
    id: UUID
    user_id: UUID
    project_id: UUID
    actor_id: UUID | None
    kind: NotificationKind
    payload: NotificationPayload
    read_at: datetime | None
    created_at: datetime

    @property
    def is_read(self) -> bool:
        return self.read_at is not None

from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import datetime
from uuid import UUID

from app.modules.notifications.domains.notification.entity import Notification
from app.modules.notifications.domains.notification_list_item.entity import NotificationListItem


class NotificationRepository(ABC):
    @abstractmethod
    async def add_all(self, notifications: Sequence[Notification]) -> None: ...

    @abstractmethod
    async def list_for_user(
        self,
        user_id: UUID,
        project_ids: frozenset[UUID],
        is_unread_only: bool,
        cursor: UUID | None,
        limit: int,
    ) -> list[NotificationListItem]: ...

    @abstractmethod
    async def count_unread(self, user_id: UUID, project_ids: frozenset[UUID]) -> int: ...

    @abstractmethod
    async def find_for_user(self, notification_id: UUID, user_id: UUID) -> Notification | None: ...

    @abstractmethod
    async def mark_read(self, notification_id: UUID, now: datetime) -> None: ...

    @abstractmethod
    async def mark_all_read(self, user_id: UUID, now: datetime) -> int: ...

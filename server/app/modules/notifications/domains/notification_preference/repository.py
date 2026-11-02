from abc import ABC, abstractmethod
from collections.abc import Collection, Sequence
from uuid import UUID

from app.modules.notifications.domains.notification_preference.entity import NotificationPreference
from app.modules.notifications.typing.enums import NotificationKind


class NotificationPreferenceRepository(ABC):
    @abstractmethod
    async def list_for_user(self, user_id: UUID) -> list[NotificationPreference]: ...

    @abstractmethod
    async def list_for_users(
        self, user_ids: Collection[UUID], kind: NotificationKind
    ) -> list[NotificationPreference]: ...

    @abstractmethod
    async def save_all(self, preferences: Sequence[NotificationPreference]) -> None: ...

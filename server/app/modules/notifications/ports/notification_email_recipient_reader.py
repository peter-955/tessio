from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.notifications.domains.notification_email_recipient.entity import NotificationEmailRecipient


class NotificationEmailRecipientReader(ABC):
    @abstractmethod
    async def find_active_recipient(self, user_id: UUID, project_id: UUID) -> NotificationEmailRecipient | None: ...

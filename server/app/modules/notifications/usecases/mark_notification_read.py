from datetime import UTC, datetime
from uuid import UUID

from app.modules.notifications.domains.notification.repository import NotificationRepository
from app.modules.notifications.errors import NotificationNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor


class MarkNotificationReadUseCase:
    def __init__(self, transaction: Transaction, notification_repository: NotificationRepository) -> None:
        self._transaction = transaction
        self._notification_repository = notification_repository

    async def execute(self, actor: Actor, notification_id: UUID) -> None:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            notification = await self._notification_repository.find_for_user(notification_id, actor.user_id)
            if notification is None:
                raise NotificationNotFoundError
            if not notification.is_read:
                await self._notification_repository.mark_read(notification.id, now)

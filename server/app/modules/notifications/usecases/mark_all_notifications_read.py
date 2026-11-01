from datetime import UTC, datetime

from app.modules.notifications.domains.notification.repository import NotificationRepository
from app.shared.common import Transaction
from app.shared.permissions import Actor


class MarkAllNotificationsReadUseCase:
    def __init__(self, transaction: Transaction, notification_repository: NotificationRepository) -> None:
        self._transaction = transaction
        self._notification_repository = notification_repository

    async def execute(self, actor: Actor) -> int:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            return await self._notification_repository.mark_all_read(actor.user_id, now)

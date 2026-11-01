from datetime import datetime

from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.shared.common import Transaction


class DeleteExpiredSessionsUseCase:
    def __init__(self, transaction: Transaction, user_session_repository: UserSessionRepository) -> None:
        self._transaction = transaction
        self._user_session_repository = user_session_repository

    async def execute(self, now: datetime) -> int:
        async with self._transaction.begin():
            return await self._user_session_repository.delete_expired(now)

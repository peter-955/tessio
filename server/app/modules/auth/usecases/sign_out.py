from uuid import UUID

from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.shared.common import Transaction


class SignOutUseCase:
    def __init__(self, transaction: Transaction, user_session_repository: UserSessionRepository) -> None:
        self._transaction = transaction
        self._user_session_repository = user_session_repository

    async def execute(self, user_session_id: UUID) -> None:
        async with self._transaction.begin():
            await self._user_session_repository.delete(user_session_id)

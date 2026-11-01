from uuid import UUID

from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.shared.common import Transaction


class SignOutAllUseCase:
    def __init__(self, transaction: Transaction, user_session_repository: UserSessionRepository) -> None:
        self._transaction = transaction
        self._user_session_repository = user_session_repository

    async def execute(self, user_id: UUID) -> None:
        async with self._transaction.begin():
            await self._user_session_repository.delete_all_for_user(user_id)

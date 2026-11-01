from uuid import UUID

from app.modules.auth.errors import UserNotFoundError
from app.modules.users import User, UserRepository
from app.shared.common import Transaction
from app.shared.permissions import Actor, WorkspaceCapability, require_workspace


class GetWorkspaceUserUseCase:
    def __init__(self, transaction: Transaction, user_repository: UserRepository) -> None:
        self._transaction = transaction
        self._user_repository = user_repository

    async def execute(self, actor: Actor, user_id: UUID) -> User:
        require_workspace(actor, WorkspaceCapability.USER_MANAGE)
        async with self._transaction.begin():
            user = await self._user_repository.find_by_id(user_id)
        if user is None:
            raise UserNotFoundError
        return user

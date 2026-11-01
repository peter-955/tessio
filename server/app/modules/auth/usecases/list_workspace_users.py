from app.modules.users import User, UserRepository, UserStatus, WorkspaceRole
from app.shared.common import Transaction
from app.shared.permissions import Actor, WorkspaceCapability, require_workspace


class ListWorkspaceUsersUseCase:
    def __init__(self, transaction: Transaction, user_repository: UserRepository) -> None:
        self._transaction = transaction
        self._user_repository = user_repository

    async def execute(
        self, actor: Actor, status: UserStatus | None, workspace_role: WorkspaceRole | None, query: str | None
    ) -> list[User]:
        require_workspace(actor, WorkspaceCapability.USER_MANAGE)
        normalized_query = None if query is None else query.strip() or None
        async with self._transaction.begin():
            return await self._user_repository.list(status, workspace_role, normalized_query)

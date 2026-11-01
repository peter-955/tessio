from uuid import UUID

from app.modules.auth.errors import OwnerOnlyError, UserNotFoundError
from app.modules.auth.utils.user_management import ensure_can_manage_user
from app.modules.users import User, UserRepository, WorkspaceRole
from app.shared.common import Transaction
from app.shared.permissions import WORKSPACE_ROLE_CAPABILITIES, Actor, WorkspaceCapability, require_workspace


class ChangeWorkspaceRoleUseCase:
    def __init__(self, transaction: Transaction, user_repository: UserRepository) -> None:
        self._transaction = transaction
        self._user_repository = user_repository

    async def execute(self, actor: Actor, user_id: UUID, workspace_role: WorkspaceRole) -> User:
        require_workspace(actor, WorkspaceCapability.USER_MANAGE)
        if WorkspaceCapability.WORKSPACE_ROLE_MANAGE not in WORKSPACE_ROLE_CAPABILITIES[actor.workspace_role]:
            raise OwnerOnlyError
        if workspace_role is WorkspaceRole.OWNER:
            raise OwnerOnlyError
        async with self._transaction.begin():
            user = await self._user_repository.find_by_id_for_update(user_id)
            if user is None:
                raise UserNotFoundError
            ensure_can_manage_user(actor, user)
            if user.workspace_role is workspace_role:
                return user
            changed_user = user.model_copy(update={"workspace_role": workspace_role})
            await self._user_repository.update(user, changed_user)
        return changed_user

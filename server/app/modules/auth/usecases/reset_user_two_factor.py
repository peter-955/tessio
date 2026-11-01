from uuid import UUID

from app.modules.auth.domains.recovery_code.repository import RecoveryCodeRepository
from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.modules.auth.errors import UserNotFoundError
from app.modules.auth.utils.two_factor import clear_two_factor
from app.modules.auth.utils.user_management import ensure_can_manage_user
from app.modules.users import User, UserRepository
from app.shared.common import Transaction
from app.shared.permissions import Actor, WorkspaceCapability, require_workspace


class ResetUserTwoFactorUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        user_session_repository: UserSessionRepository,
        recovery_code_repository: RecoveryCodeRepository,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._user_session_repository = user_session_repository
        self._recovery_code_repository = recovery_code_repository

    async def execute(self, actor: Actor, user_id: UUID) -> User:
        require_workspace(actor, WorkspaceCapability.USER_MANAGE)
        async with self._transaction.begin():
            user = await self._user_repository.find_by_id_for_update(user_id)
            if user is None:
                raise UserNotFoundError
            ensure_can_manage_user(actor, user)
            reset_user = clear_two_factor(user)
            await self._user_repository.update(user, reset_user)
            await self._recovery_code_repository.replace_for_user(user.id, [])
            await self._user_session_repository.delete_all_for_user(user.id)
        return reset_user

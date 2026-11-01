from datetime import UTC, datetime
from uuid import UUID

from app.modules.auth.domains.one_time_token.repository import OneTimeTokenRepository
from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.modules.auth.errors import UserNotFoundError
from app.modules.auth.ports.api_token_revoker import ApiTokenRevoker
from app.modules.auth.typing.enums import OneTimeTokenPurpose
from app.modules.auth.utils.user_management import ensure_can_manage_user
from app.modules.users import User, UserRepository, UserStatus
from app.shared.common import Transaction
from app.shared.permissions import Actor, WorkspaceCapability, require_workspace


class DeactivateUserUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        user_session_repository: UserSessionRepository,
        one_time_token_repository: OneTimeTokenRepository,
        api_token_revoker: ApiTokenRevoker,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._user_session_repository = user_session_repository
        self._one_time_token_repository = one_time_token_repository
        self._api_token_revoker = api_token_revoker

    async def execute(self, actor: Actor, user_id: UUID) -> User:
        require_workspace(actor, WorkspaceCapability.USER_MANAGE)
        now = datetime.now(UTC)
        async with self._transaction.begin():
            user = await self._user_repository.find_by_id_for_update(user_id)
            if user is None:
                raise UserNotFoundError
            ensure_can_manage_user(actor, user)
            if user.status is UserStatus.DEACTIVATED:
                return user
            deactivated_user = user.model_copy(update={"status": UserStatus.DEACTIVATED, "deactivated_at": now})
            await self._user_repository.update(user, deactivated_user)
            await self._user_session_repository.delete_all_for_user(user.id)
            for purpose in (OneTimeTokenPurpose.INVITE, OneTimeTokenPurpose.PASSWORD_RESET):
                await self._one_time_token_repository.expire_unused_for_user(user.id, purpose, now)
            await self._api_token_revoker.revoke_all_for_user(user.id, now)
        return deactivated_user

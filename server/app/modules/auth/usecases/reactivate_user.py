from datetime import UTC, datetime
from uuid import UUID

from app.modules.auth.domains.one_time_token.repository import OneTimeTokenRepository
from app.modules.auth.errors import UserNotFoundError
from app.modules.auth.typing.enums import OneTimeTokenPurpose
from app.modules.auth.utils.invite import build_invite, build_invite_url
from app.modules.auth.utils.invite_email import build_invite_email
from app.modules.auth.utils.sign_in_attempt import clear_failed_sign_ins
from app.modules.auth.utils.user_management import ensure_can_manage_user
from app.modules.users import User, UserRepository, UserStatus
from app.shared.common import Transaction
from app.shared.mailer import Mailer
from app.shared.permissions import Actor, WorkspaceCapability, require_workspace


class ReactivateUserUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        one_time_token_repository: OneTimeTokenRepository,
        mailer: Mailer,
        client_url: str,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._one_time_token_repository = one_time_token_repository
        self._mailer = mailer
        self._client_url = client_url

    async def execute(self, actor: Actor, user_id: UUID) -> User:
        require_workspace(actor, WorkspaceCapability.USER_MANAGE)
        now = datetime.now(UTC)
        invite_token: str | None = None
        async with self._transaction.begin():
            user = await self._user_repository.find_by_id_for_update(user_id)
            if user is None:
                raise UserNotFoundError
            ensure_can_manage_user(actor, user)
            if user.status is not UserStatus.DEACTIVATED:
                return user
            is_invite_pending = user.password_hash is None
            reactivated_user = clear_failed_sign_ins(user).model_copy(
                update={
                    "status": UserStatus.INVITED if is_invite_pending else UserStatus.ACTIVE,
                    "deactivated_at": None,
                }
            )
            await self._user_repository.update(user, reactivated_user)
            if is_invite_pending:
                invite, invite_token = build_invite(user.id, now)
                await self._one_time_token_repository.expire_unused_for_user(user.id, OneTimeTokenPurpose.INVITE, now)
                await self._one_time_token_repository.save(invite)
        if invite_token is not None:
            await self._mailer.send(
                build_invite_email(
                    reactivated_user.email, reactivated_user.name, build_invite_url(self._client_url, invite_token)
                )
            )
        return reactivated_user

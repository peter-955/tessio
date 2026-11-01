from datetime import UTC, datetime
from uuid import UUID

from app.modules.auth.domains.one_time_token.repository import OneTimeTokenRepository
from app.modules.auth.errors import UserNotFoundError, UserNotInvitedError
from app.modules.auth.typing.enums import OneTimeTokenPurpose
from app.modules.auth.utils.invite import build_invite, build_invite_url
from app.modules.auth.utils.invite_email import build_invite_email
from app.modules.users import UserRepository, UserStatus
from app.shared.common import Transaction
from app.shared.mailer import Mailer
from app.shared.permissions import Actor, WorkspaceCapability, require_workspace


class ResendInviteUseCase:
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

    async def execute(self, actor: Actor, user_id: UUID) -> None:
        require_workspace(actor, WorkspaceCapability.USER_MANAGE)
        now = datetime.now(UTC)
        async with self._transaction.begin():
            user = await self._user_repository.find_by_id(user_id)
            if user is None:
                raise UserNotFoundError
            if user.status is not UserStatus.INVITED:
                raise UserNotInvitedError
            invite, token = build_invite(user.id, now)
            await self._one_time_token_repository.expire_unused_for_user(user.id, OneTimeTokenPurpose.INVITE, now)
            await self._one_time_token_repository.save(invite)
        await self._mailer.send(build_invite_email(user.email, user.name, build_invite_url(self._client_url, token)))

from datetime import UTC, datetime
from uuid import uuid7

from app.modules.auth.domains.one_time_token.repository import OneTimeTokenRepository
from app.modules.auth.errors import EmailAlreadyUsedError
from app.modules.auth.utils.email_address import normalize_email
from app.modules.auth.utils.invite import build_invite, build_invite_url
from app.modules.auth.utils.invite_email import build_invite_email
from app.modules.users import User, UserRepository, UserStatus, WorkspaceRole
from app.shared.common import Transaction
from app.shared.mailer import Mailer


class InviteUserUseCase:
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

    async def execute(self, email: str, name: str, workspace_role: WorkspaceRole) -> User:
        now = datetime.now(UTC)
        user = User(
            id=uuid7(),
            email=normalize_email(email),
            name=name.strip(),
            workspace_role=workspace_role,
            status=UserStatus.INVITED,
            password_hash=None,
            totp_key_encrypted=None,
            totp_confirmed_at=None,
            totp_last_time_step=None,
            failed_sign_ins=0,
            locked_until=None,
            created_at=now,
        )
        invite, token = build_invite(user.id, now)
        async with self._transaction.begin():
            if await self._user_repository.find_by_email(user.email) is not None:
                raise EmailAlreadyUsedError
            await self._user_repository.add(user)
            await self._one_time_token_repository.save(invite)
        await self._mailer.send(build_invite_email(user.email, user.name, build_invite_url(self._client_url, token)))
        return user

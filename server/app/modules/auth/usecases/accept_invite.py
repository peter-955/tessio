from datetime import UTC, datetime

from app.modules.auth.domains.issued_session.entity import IssuedSession
from app.modules.auth.domains.one_time_token.repository import OneTimeTokenRepository
from app.modules.auth.domains.session_client.entity import SessionClient
from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.modules.auth.errors import BreachedPasswordError, InvalidOneTimeLinkError, WeakPasswordError
from app.modules.auth.ports.breached_password_checker import BreachedPasswordChecker
from app.modules.auth.ports.password_hasher import PasswordHasher
from app.modules.auth.typing.enums import OneTimeTokenPurpose, SignInStep
from app.modules.auth.utils.password_policy import is_password_strong
from app.modules.auth.utils.secret_token import hash_secret_token
from app.modules.auth.utils.user_session import start_half_session
from app.modules.users import UserRepository, UserStatus
from app.shared.common import Transaction


class AcceptInviteUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        one_time_token_repository: OneTimeTokenRepository,
        user_session_repository: UserSessionRepository,
        password_hasher: PasswordHasher,
        breached_password_checker: BreachedPasswordChecker,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._one_time_token_repository = one_time_token_repository
        self._user_session_repository = user_session_repository
        self._password_hasher = password_hasher
        self._breached_password_checker = breached_password_checker

    async def execute(self, token: str, password: str, client: SessionClient) -> IssuedSession:
        if not is_password_strong(password):
            raise WeakPasswordError
        if await self._breached_password_checker.is_breached(password):
            raise BreachedPasswordError
        password_hash = await self._password_hasher.hash_password(password)
        now = datetime.now(UTC)
        async with self._transaction.begin():
            invite = await self._one_time_token_repository.find_by_token_hash(
                hash_secret_token(token), OneTimeTokenPurpose.INVITE
            )
            if invite is None or not invite.is_usable(now):
                raise InvalidOneTimeLinkError
            user = await self._user_repository.find_by_id_for_update(invite.user_id)
            if user is None or user.status is not UserStatus.INVITED:
                raise InvalidOneTimeLinkError
            await self._user_repository.update(
                user, user.model_copy(update={"status": UserStatus.ACTIVE, "password_hash": password_hash})
            )
            await self._one_time_token_repository.save(invite.model_copy(update={"used_at": now}))
            user_session, session_token = start_half_session(user.id, client, now)
            await self._user_session_repository.save(user_session)
        return IssuedSession(token=session_token, next_step=SignInStep.TWO_FACTOR_SETUP_REQUIRED)

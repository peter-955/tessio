from datetime import UTC, datetime

from app.modules.auth.domains.one_time_token.repository import OneTimeTokenRepository
from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.modules.auth.errors import BreachedPasswordError, InvalidOneTimeLinkError, WeakPasswordError
from app.modules.auth.ports.breached_password_checker import BreachedPasswordChecker
from app.modules.auth.ports.password_hasher import PasswordHasher
from app.modules.auth.typing.enums import OneTimeTokenPurpose
from app.modules.auth.utils.password_policy import is_password_strong
from app.modules.auth.utils.secret_token import hash_secret_token
from app.modules.auth.utils.sign_in_attempt import clear_failed_sign_ins
from app.modules.users import UserRepository, UserStatus
from app.shared.common import Transaction


class ResetPasswordUseCase:
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

    async def execute(self, token: str, password: str) -> None:
        if not is_password_strong(password):
            raise WeakPasswordError
        if await self._breached_password_checker.is_breached(password):
            raise BreachedPasswordError
        password_hash = await self._password_hasher.hash_password(password)
        now = datetime.now(UTC)
        async with self._transaction.begin():
            reset = await self._one_time_token_repository.find_by_token_hash(
                hash_secret_token(token), OneTimeTokenPurpose.PASSWORD_RESET
            )
            if reset is None or not reset.is_usable(now):
                raise InvalidOneTimeLinkError
            user = await self._user_repository.find_by_id_for_update(reset.user_id)
            if user is None or user.status is not UserStatus.ACTIVE:
                raise InvalidOneTimeLinkError
            await self._user_repository.update(
                user, clear_failed_sign_ins(user).model_copy(update={"password_hash": password_hash})
            )
            await self._one_time_token_repository.save(reset.model_copy(update={"used_at": now}))
            await self._user_session_repository.delete_all_for_user(user.id)

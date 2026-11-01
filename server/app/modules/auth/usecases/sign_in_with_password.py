from datetime import UTC, datetime

from app.modules.auth.domains.issued_session.entity import IssuedSession
from app.modules.auth.domains.session_client.entity import SessionClient
from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.modules.auth.errors import InvalidCredentialsError, SignInLockedError
from app.modules.auth.ports.password_hasher import PasswordHasher
from app.modules.auth.typing.constants.auth_policy import DUMMY_PASSWORD_HASH
from app.modules.auth.typing.enums import SignInStep
from app.modules.auth.utils.email_address import normalize_email
from app.modules.auth.utils.sign_in_attempt import record_failed_sign_in
from app.modules.auth.utils.user_session import start_half_session
from app.modules.users import UserRepository, UserStatus
from app.shared.common import Transaction


class SignInWithPasswordUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        user_session_repository: UserSessionRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._user_session_repository = user_session_repository
        self._password_hasher = password_hasher

    async def execute(self, email: str, password: str, client: SessionClient) -> IssuedSession:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            user = await self._user_repository.find_by_email(normalize_email(email))
            if user is None or user.status is not UserStatus.ACTIVE or user.password_hash is None:
                await self._password_hasher.verify_password(DUMMY_PASSWORD_HASH, password)
                raise InvalidCredentialsError
            if user.is_locked(now):
                raise SignInLockedError
            is_password_correct = await self._password_hasher.verify_password(user.password_hash, password)
            if is_password_correct:
                user_session, session_token = start_half_session(user.id, client, now)
                await self._user_session_repository.save(user_session)
            else:
                current_user = await self._user_repository.find_by_id_for_update(user.id)
                if current_user is not None:
                    await self._user_repository.update(current_user, record_failed_sign_in(current_user, now))
        if not is_password_correct:
            raise InvalidCredentialsError
        next_step = (
            SignInStep.TWO_FACTOR_REQUIRED if user.is_two_factor_set_up else SignInStep.TWO_FACTOR_SETUP_REQUIRED
        )
        return IssuedSession(token=session_token, next_step=next_step)

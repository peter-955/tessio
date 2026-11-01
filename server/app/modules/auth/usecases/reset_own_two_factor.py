from datetime import UTC, datetime

from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.domains.issued_session.entity import IssuedSession
from app.modules.auth.domains.recovery_code.repository import RecoveryCodeRepository
from app.modules.auth.domains.session_client.entity import SessionClient
from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.modules.auth.errors import TwoFactorSetupNotStartedError
from app.modules.auth.ports.password_hasher import PasswordHasher
from app.modules.auth.typing.enums import SignInStep
from app.modules.auth.utils.active_user import lock_active_user
from app.modules.auth.utils.current_password import ensure_current_password
from app.modules.auth.utils.two_factor import clear_two_factor
from app.modules.auth.utils.user_session import start_half_session
from app.modules.users import UserRepository
from app.shared.common import Transaction


class ResetOwnTwoFactorUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        user_session_repository: UserSessionRepository,
        recovery_code_repository: RecoveryCodeRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._user_session_repository = user_session_repository
        self._recovery_code_repository = recovery_code_repository
        self._password_hasher = password_hasher

    async def execute(self, authenticated: AuthenticatedSession, password: str, client: SessionClient) -> IssuedSession:
        user = authenticated.user
        if not user.is_two_factor_set_up:
            raise TwoFactorSetupNotStartedError
        await ensure_current_password(self._password_hasher, user, password)
        now = datetime.now(UTC)
        user_session, session_token = start_half_session(user.id, client, now)
        async with self._transaction.begin():
            current_user = await lock_active_user(self._user_repository, user.id)
            await self._user_repository.update(current_user, clear_two_factor(current_user))
            await self._recovery_code_repository.replace_for_user(user.id, [])
            await self._user_session_repository.delete_all_for_user(user.id)
            await self._user_session_repository.save(user_session)
        return IssuedSession(token=session_token, next_step=SignInStep.TWO_FACTOR_SETUP_REQUIRED)

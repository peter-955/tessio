from datetime import UTC, datetime

from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.domains.issued_session.entity import IssuedSession
from app.modules.auth.domains.recovery_code.repository import RecoveryCodeRepository
from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.modules.auth.errors import InvalidTwoFactorCodeError, SignInLockedError, TwoFactorSetupNotStartedError
from app.modules.auth.ports.totp_authenticator import TotpAuthenticator
from app.modules.auth.typing.enums import SignInStep
from app.modules.auth.utils.active_user import lock_active_user
from app.modules.auth.utils.recovery_code import normalize_recovery_code
from app.modules.auth.utils.secret_token import hash_secret_token
from app.modules.auth.utils.sign_in_attempt import clear_failed_sign_ins, record_failed_sign_in
from app.modules.auth.utils.user_session import complete_two_factor
from app.modules.users import User, UserRepository
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher


class VerifyTwoFactorUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        user_session_repository: UserSessionRepository,
        recovery_code_repository: RecoveryCodeRepository,
        totp_authenticator: TotpAuthenticator,
        secret_cipher: SecretCipher,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._user_session_repository = user_session_repository
        self._recovery_code_repository = recovery_code_repository
        self._totp_authenticator = totp_authenticator
        self._secret_cipher = secret_cipher

    async def execute(self, authenticated: AuthenticatedSession, code: str) -> IssuedSession:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            user = await lock_active_user(self._user_repository, authenticated.user.id)
            if not user.is_two_factor_set_up or user.totp_key_encrypted is None:
                raise TwoFactorSetupNotStartedError
            if user.is_locked(now):
                raise SignInLockedError
            key = self._secret_cipher.decrypt(user.totp_key_encrypted).decode()
            time_step = self._totp_authenticator.find_time_step(key, code, now)
            is_code_accepted = await self._accept_code(user, code, time_step, now)
            if is_code_accepted:
                user_session, session_token = complete_two_factor(authenticated.user_session, now)
                await self._user_session_repository.save(user_session)
            else:
                await self._record_failed_code(user, authenticated, now)
        if not is_code_accepted:
            raise InvalidTwoFactorCodeError
        return IssuedSession(token=session_token, next_step=SignInStep.SIGNED_IN)

    async def _accept_code(self, user: User, code: str, time_step: int | None, now: datetime) -> bool:
        if time_step is not None and (user.totp_last_time_step is None or time_step > user.totp_last_time_step):
            await self._user_repository.update(
                user, clear_failed_sign_ins(user).model_copy(update={"totp_last_time_step": time_step})
            )
            return True
        recovery_code = await self._recovery_code_repository.find_unused(
            user.id, hash_secret_token(normalize_recovery_code(code))
        )
        if recovery_code is None:
            return False
        await self._recovery_code_repository.save(recovery_code.model_copy(update={"used_at": now}))
        await self._user_repository.update(user, clear_failed_sign_ins(user))
        return True

    async def _record_failed_code(self, user: User, authenticated: AuthenticatedSession, now: datetime) -> None:
        failed_user = record_failed_sign_in(user, now)
        await self._user_repository.update(user, failed_user)
        if failed_user.is_locked(now):
            await self._user_session_repository.delete(authenticated.user_session.id)

from datetime import UTC, datetime

from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.domains.confirmed_two_factor.entity import ConfirmedTwoFactor
from app.modules.auth.domains.issued_session.entity import IssuedSession
from app.modules.auth.domains.recovery_code.repository import RecoveryCodeRepository
from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.modules.auth.errors import InvalidTwoFactorCodeError, TwoFactorAlreadySetUpError, TwoFactorSetupNotStartedError
from app.modules.auth.ports.totp_authenticator import TotpAuthenticator
from app.modules.auth.typing.constants.auth_policy import RECOVERY_CODE_COUNT
from app.modules.auth.typing.enums import SignInStep
from app.modules.auth.utils.active_user import lock_active_user
from app.modules.auth.utils.recovery_code import build_recovery_code, generate_recovery_code
from app.modules.auth.utils.user_session import complete_two_factor
from app.modules.users import UserRepository
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher


class ConfirmTwoFactorSetupUseCase:
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

    async def execute(self, authenticated: AuthenticatedSession, code: str) -> ConfirmedTwoFactor:
        user = authenticated.user
        if user.is_two_factor_set_up:
            raise TwoFactorAlreadySetUpError
        if user.totp_key_encrypted is None:
            raise TwoFactorSetupNotStartedError
        now = datetime.now(UTC)
        key = self._secret_cipher.decrypt(user.totp_key_encrypted).decode()
        time_step = self._totp_authenticator.find_time_step(key, code, now)
        if time_step is None:
            raise InvalidTwoFactorCodeError
        recovery_codes = [generate_recovery_code() for _ in range(RECOVERY_CODE_COUNT)]
        user_session, session_token = complete_two_factor(authenticated.user_session, now)
        async with self._transaction.begin():
            current_user = await lock_active_user(self._user_repository, user.id)
            if current_user.is_two_factor_set_up:
                raise TwoFactorAlreadySetUpError
            if current_user.totp_key_encrypted != user.totp_key_encrypted:
                raise InvalidTwoFactorCodeError
            await self._user_repository.update(
                current_user,
                current_user.model_copy(update={"totp_confirmed_at": now, "totp_last_time_step": time_step}),
            )
            await self._recovery_code_repository.replace_for_user(
                user.id, [build_recovery_code(user.id, recovery_code, now) for recovery_code in recovery_codes]
            )
            await self._user_session_repository.save(user_session)
        return ConfirmedTwoFactor(
            issued_session=IssuedSession(token=session_token, next_step=SignInStep.SIGNED_IN),
            recovery_codes=recovery_codes,
        )

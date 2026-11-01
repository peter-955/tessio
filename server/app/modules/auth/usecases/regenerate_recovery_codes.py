from datetime import UTC, datetime

from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.domains.recovery_code.repository import RecoveryCodeRepository
from app.modules.auth.errors import TwoFactorSetupNotStartedError
from app.modules.auth.ports.password_hasher import PasswordHasher
from app.modules.auth.typing.constants.auth_policy import RECOVERY_CODE_COUNT
from app.modules.auth.utils.current_password import ensure_current_password
from app.modules.auth.utils.recovery_code import build_recovery_code, generate_recovery_code
from app.shared.common import Transaction


class RegenerateRecoveryCodesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        recovery_code_repository: RecoveryCodeRepository,
        password_hasher: PasswordHasher,
    ) -> None:
        self._transaction = transaction
        self._recovery_code_repository = recovery_code_repository
        self._password_hasher = password_hasher

    async def execute(self, authenticated: AuthenticatedSession, password: str) -> list[str]:
        user = authenticated.user
        if not user.is_two_factor_set_up:
            raise TwoFactorSetupNotStartedError
        await ensure_current_password(self._password_hasher, user, password)
        now = datetime.now(UTC)
        recovery_codes = [generate_recovery_code() for _ in range(RECOVERY_CODE_COUNT)]
        async with self._transaction.begin():
            await self._recovery_code_repository.replace_for_user(
                user.id, [build_recovery_code(user.id, recovery_code, now) for recovery_code in recovery_codes]
            )
        return recovery_codes

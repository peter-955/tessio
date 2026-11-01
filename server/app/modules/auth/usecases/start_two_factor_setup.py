from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.domains.two_factor_setup.entity import TwoFactorSetup
from app.modules.auth.errors import TwoFactorAlreadySetUpError
from app.modules.auth.ports.totp_authenticator import TotpAuthenticator
from app.modules.auth.utils.active_user import lock_active_user
from app.modules.users import UserRepository
from app.shared.common import Transaction
from app.shared.crypto import SecretCipher


class StartTwoFactorSetupUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        totp_authenticator: TotpAuthenticator,
        secret_cipher: SecretCipher,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._totp_authenticator = totp_authenticator
        self._secret_cipher = secret_cipher

    async def execute(self, authenticated: AuthenticatedSession) -> TwoFactorSetup:
        user = authenticated.user
        if user.is_two_factor_set_up:
            raise TwoFactorAlreadySetUpError
        key = self._totp_authenticator.generate_key()
        async with self._transaction.begin():
            current_user = await lock_active_user(self._user_repository, user.id)
            if current_user.is_two_factor_set_up:
                raise TwoFactorAlreadySetUpError
            await self._user_repository.update(
                current_user,
                current_user.model_copy(update={"totp_key_encrypted": self._secret_cipher.encrypt(key.encode())}),
            )
        return TwoFactorSetup(key=key, setup_uri=self._totp_authenticator.build_setup_uri(key, user.email))

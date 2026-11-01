from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.modules.auth.errors import BreachedPasswordError, WeakPasswordError
from app.modules.auth.ports.breached_password_checker import BreachedPasswordChecker
from app.modules.auth.ports.password_hasher import PasswordHasher
from app.modules.auth.utils.active_user import lock_active_user
from app.modules.auth.utils.current_password import ensure_current_password
from app.modules.auth.utils.password_policy import is_password_strong
from app.modules.users import UserRepository
from app.shared.common import Transaction


class ChangePasswordUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        user_session_repository: UserSessionRepository,
        password_hasher: PasswordHasher,
        breached_password_checker: BreachedPasswordChecker,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._user_session_repository = user_session_repository
        self._password_hasher = password_hasher
        self._breached_password_checker = breached_password_checker

    async def execute(self, authenticated: AuthenticatedSession, current_password: str, new_password: str) -> None:
        user = authenticated.user
        await ensure_current_password(self._password_hasher, user, current_password)
        if not is_password_strong(new_password):
            raise WeakPasswordError
        if await self._breached_password_checker.is_breached(new_password):
            raise BreachedPasswordError
        password_hash = await self._password_hasher.hash_password(new_password)
        async with self._transaction.begin():
            current_user = await lock_active_user(self._user_repository, user.id)
            await self._user_repository.update(
                current_user, current_user.model_copy(update={"password_hash": password_hash})
            )
            await self._user_session_repository.delete_all_for_user_except(user.id, authenticated.user_session.id)

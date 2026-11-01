from datetime import UTC, datetime

from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.domains.user_session.repository import UserSessionRepository
from app.modules.auth.errors import NotSignedInError
from app.modules.auth.typing.constants.auth_policy import LAST_SEEN_REFRESH_INTERVAL, SESSION_IDLE_LIFETIME
from app.modules.auth.utils.secret_token import hash_secret_token
from app.modules.users import UserRepository, UserStatus
from app.shared.common import Transaction


class AuthenticateSessionUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        user_session_repository: UserSessionRepository,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._user_session_repository = user_session_repository

    async def execute(self, token: str) -> AuthenticatedSession:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            user_session = await self._user_session_repository.find_by_token_hash(hash_secret_token(token))
            if user_session is None or user_session.is_expired(now):
                raise NotSignedInError
            user = await self._user_repository.find_by_id(user_session.user_id)
            if user is None or user.status is not UserStatus.ACTIVE:
                raise NotSignedInError
            if user_session.is_two_factor_passed and now - user_session.last_seen_at >= LAST_SEEN_REFRESH_INTERVAL:
                user_session = user_session.model_copy(
                    update={"last_seen_at": now, "expires_at": now + SESSION_IDLE_LIFETIME}
                )
                await self._user_session_repository.save(user_session)
        return AuthenticatedSession(user_session=user_session, user=user)

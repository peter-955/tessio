from datetime import UTC, datetime
from uuid import uuid7

from app.modules.auth.domains.one_time_token.entity import OneTimeToken
from app.modules.auth.domains.one_time_token.repository import OneTimeTokenRepository
from app.modules.auth.typing.constants.auth_policy import PASSWORD_RESET_LIFETIME
from app.modules.auth.typing.constants.rate_limit import PASSWORD_FORGOT_EMAIL_RATE_LIMIT
from app.modules.auth.typing.enums import OneTimeTokenPurpose
from app.modules.auth.utils.email_address import hash_email, normalize_email
from app.modules.auth.utils.password_reset_email import build_password_reset_email
from app.modules.auth.utils.secret_token import generate_secret_token, hash_secret_token
from app.modules.users import UserRepository, UserStatus
from app.shared.common import Transaction
from app.shared.mailer import Mailer
from app.shared.rate_limit import RateLimiter


class RequestPasswordResetUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        one_time_token_repository: OneTimeTokenRepository,
        rate_limiter: RateLimiter,
        mailer: Mailer,
        client_url: str,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._one_time_token_repository = one_time_token_repository
        self._rate_limiter = rate_limiter
        self._mailer = mailer
        self._client_url = client_url

    async def execute(self, email: str) -> None:
        decision = await self._rate_limiter.hit(hash_email(email), PASSWORD_FORGOT_EMAIL_RATE_LIMIT)
        if not decision.is_allowed:
            return
        now = datetime.now(UTC)
        token = generate_secret_token()
        async with self._transaction.begin():
            user = await self._user_repository.find_by_email(normalize_email(email))
            if user is None or user.status is not UserStatus.ACTIVE:
                return
            await self._one_time_token_repository.save(
                OneTimeToken(
                    id=uuid7(),
                    user_id=user.id,
                    purpose=OneTimeTokenPurpose.PASSWORD_RESET,
                    token_hash=hash_secret_token(token),
                    expires_at=now + PASSWORD_RESET_LIFETIME,
                    used_at=None,
                    created_at=now,
                )
            )
        await self._mailer.send(
            build_password_reset_email(user.email, user.name, f"{self._client_url}/reset-password/{token}")
        )

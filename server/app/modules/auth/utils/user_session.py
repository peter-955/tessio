from datetime import datetime
from uuid import UUID, uuid7

from app.modules.auth.domains.session_client.entity import SessionClient
from app.modules.auth.domains.user_session.entity import UserSession
from app.modules.auth.typing.constants.auth_policy import HALF_SESSION_LIFETIME, SESSION_IDLE_LIFETIME
from app.modules.auth.utils.secret_token import generate_secret_token, hash_secret_token


def start_half_session(user_id: UUID, client: SessionClient, now: datetime) -> tuple[UserSession, str]:
    token = generate_secret_token()
    user_session = UserSession(
        id=uuid7(),
        user_id=user_id,
        token_hash=hash_secret_token(token),
        is_two_factor_passed=False,
        user_agent=client.user_agent,
        ip=client.ip,
        last_seen_at=now,
        expires_at=now + HALF_SESSION_LIFETIME,
        created_at=now,
    )
    return user_session, token


def complete_two_factor(user_session: UserSession, now: datetime) -> tuple[UserSession, str]:
    token = generate_secret_token()
    completed_session = user_session.model_copy(
        update={
            "token_hash": hash_secret_token(token),
            "is_two_factor_passed": True,
            "last_seen_at": now,
            "expires_at": now + SESSION_IDLE_LIFETIME,
        }
    )
    return completed_session, token

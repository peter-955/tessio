from datetime import datetime
from uuid import UUID, uuid7

from app.modules.auth.domains.one_time_token.entity import OneTimeToken
from app.modules.auth.typing.constants.auth_policy import INVITE_LIFETIME
from app.modules.auth.typing.enums import OneTimeTokenPurpose
from app.modules.auth.utils.secret_token import generate_secret_token, hash_secret_token


def build_invite(user_id: UUID, now: datetime) -> tuple[OneTimeToken, str]:
    token = generate_secret_token()
    invite = OneTimeToken(
        id=uuid7(),
        user_id=user_id,
        purpose=OneTimeTokenPurpose.INVITE,
        token_hash=hash_secret_token(token),
        expires_at=now + INVITE_LIFETIME,
        used_at=None,
        created_at=now,
    )
    return invite, token


def build_invite_url(client_url: str, token: str) -> str:
    return f"{client_url}/invite/{token}"

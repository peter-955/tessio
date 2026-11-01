import hashlib
import secrets

from app.modules.api_tokens.typing.constants import API_CREDENTIAL_START, API_TOKEN_PREFIX_BYTES


def generate_api_token() -> tuple[str, str]:
    prefix = secrets.token_hex(API_TOKEN_PREFIX_BYTES)
    return f"{API_CREDENTIAL_START}{prefix}_{secrets.token_urlsafe(32)}", prefix


def hash_api_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

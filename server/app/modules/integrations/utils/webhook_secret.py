import secrets

from app.modules.integrations.typing.constants.webhook import (
    WEBHOOK_KEY_PREFIX,
    WEBHOOK_SECRET_BYTES,
    WEBHOOK_SECRET_HINT_LENGTH,
)


def generate_webhook_secret() -> str:
    return f"{WEBHOOK_KEY_PREFIX}{secrets.token_urlsafe(WEBHOOK_SECRET_BYTES)}"


def build_webhook_secret_hint(secret: str) -> str:
    return f"{WEBHOOK_KEY_PREFIX}…{secret[-WEBHOOK_SECRET_HINT_LENGTH:]}"

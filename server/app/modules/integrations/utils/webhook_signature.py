import hashlib
import hmac

from app.modules.integrations.typing.constants.webhook import WEBHOOK_SIGNATURE_SCHEME


def sign_webhook_body(secret: str, timestamp: int, body: bytes) -> str:
    signed_content = f"{timestamp}.".encode() + body
    digest = hmac.new(secret.encode(), signed_content, hashlib.sha256).hexdigest()
    return f"{WEBHOOK_SIGNATURE_SCHEME}={digest}"


def is_valid_webhook_signature(secret: str, timestamp: int, body: bytes, signature: str) -> bool:
    return hmac.compare_digest(sign_webhook_body(secret, timestamp, body), signature)

import hashlib
import secrets


def generate_secret_token() -> str:
    return secrets.token_urlsafe(32)


def hash_secret_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()

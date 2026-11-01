import hashlib


def normalize_email(email: str) -> str:
    return email.strip().lower()


def hash_email(email: str) -> str:
    return hashlib.sha256(normalize_email(email).encode()).hexdigest()

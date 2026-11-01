import secrets
from datetime import datetime
from uuid import UUID, uuid7

from app.modules.auth.domains.recovery_code.entity import RecoveryCode
from app.modules.auth.utils.secret_token import hash_secret_token


def generate_recovery_code() -> str:
    code = secrets.token_hex(5)
    return f"{code[:5]}-{code[5:]}"


def normalize_recovery_code(code: str) -> str:
    return code.strip().lower().replace("-", "").replace(" ", "")


def build_recovery_code(user_id: UUID, code: str, now: datetime) -> RecoveryCode:
    return RecoveryCode(
        id=uuid7(),
        user_id=user_id,
        code_hash=hash_secret_token(normalize_recovery_code(code)),
        used_at=None,
        created_at=now,
    )

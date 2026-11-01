from datetime import datetime

from app.modules.auth.typing.constants.auth_policy import LOCKOUT_DURATION, MAXIMUM_FAILED_SIGN_INS
from app.modules.users import User


def record_failed_sign_in(user: User, now: datetime) -> User:
    failed_sign_ins = user.failed_sign_ins + 1
    if failed_sign_ins >= MAXIMUM_FAILED_SIGN_INS:
        return user.model_copy(update={"failed_sign_ins": 0, "locked_until": now + LOCKOUT_DURATION})
    return user.model_copy(update={"failed_sign_ins": failed_sign_ins})


def clear_failed_sign_ins(user: User) -> User:
    return user.model_copy(update={"failed_sign_ins": 0, "locked_until": None})

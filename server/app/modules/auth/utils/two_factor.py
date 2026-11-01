from app.modules.auth.utils.sign_in_attempt import clear_failed_sign_ins
from app.modules.users import User


def clear_two_factor(user: User) -> User:
    return clear_failed_sign_ins(user).model_copy(
        update={"totp_key_encrypted": None, "totp_confirmed_at": None, "totp_last_time_step": None}
    )

from app.modules.auth.typing.constants.auth_policy import MINIMUM_PASSWORD_LENGTH


def is_password_strong(password: str) -> bool:
    return len(password) >= MINIMUM_PASSWORD_LENGTH

from enum import StrEnum


class OneTimeTokenPurpose(StrEnum):
    INVITE = "invite"
    PASSWORD_RESET = "password_reset"

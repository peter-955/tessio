from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class InvalidCredentialsError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_CREDENTIALS, "Email or password is incorrect.")


class InvalidOneTimeLinkError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_ONE_TIME_LINK, "This link is invalid or has expired.")


class WeakPasswordError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.WEAK_PASSWORD, "The password does not meet the password rules.")


class BreachedPasswordError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.PASSWORD_BREACHED, "This password appears in known data breaches. Choose another one."
        )


class SignInLockedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.SIGN_IN_LOCKED, "Too many failed attempts. Try again in 15 minutes.")


class EmailAlreadyUsedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.EMAIL_ALREADY_USED, "A user with this email already exists.")


class NotSignedInError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_SIGNED_IN, "Sign in to continue.")


class InvalidTwoFactorCodeError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_TWO_FACTOR_CODE, "The code is incorrect.")


class TwoFactorAlreadySetUpError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.TWO_FACTOR_ALREADY_SET_UP, "Two-factor authentication is already set up.")


class TwoFactorSetupNotStartedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.TWO_FACTOR_SETUP_NOT_STARTED, "Start the two-factor setup first.")


class UserNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "User not found.")


class OwnerOnlyError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.OWNER_ONLY, "Only the workspace owner can do this.")


class CannotChangeOwnOrOwnerError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.CANNOT_CHANGE_OWN_OR_OWNER, "You cannot change your own account or the owner's account here."
        )


class UserNotInvitedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.USER_NOT_INVITED, "This user has already accepted the invite.")


class InvalidCurrentPasswordError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_CURRENT_PASSWORD, "The password is incorrect.")


class AvatarNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Avatar not found.")


class UploadNotCompletedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UPLOAD_NOT_COMPLETED, "The upload is not complete yet.")

from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class NotificationNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Notification not found.")

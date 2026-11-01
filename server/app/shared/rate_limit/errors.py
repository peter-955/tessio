from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class RateLimitedError(TessioError):
    def __init__(self, retry_after_seconds: int) -> None:
        super().__init__(ErrorCode.RATE_LIMITED, "Too many attempts. Try again later.")
        self.retry_after_seconds = retry_after_seconds

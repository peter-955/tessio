from app.modules.insights.typing.constants import MAX_RANGE_DAYS
from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class InsightsRangeInvalidError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "The start date must be on or before the end date.")


class InsightsRangeTooLongError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, f"Pick a date range of at most {MAX_RANGE_DAYS} days.")

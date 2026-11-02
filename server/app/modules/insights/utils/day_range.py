from datetime import date, timedelta

from app.modules.insights.domains.day_range.entity import DayRange
from app.modules.insights.errors import InsightsRangeInvalidError, InsightsRangeTooLongError
from app.modules.insights.typing.constants import DEFAULT_RANGE_DAYS, MAX_RANGE_DAYS


def resolve_day_range(first_day: date | None, last_day: date | None, today: date) -> DayRange:
    resolved_last_day = last_day or (today if first_day is None else max(first_day, today))
    resolved_first_day = first_day or resolved_last_day - timedelta(days=DEFAULT_RANGE_DAYS - 1)
    if resolved_first_day > resolved_last_day:
        raise InsightsRangeInvalidError
    if (resolved_last_day - resolved_first_day).days + 1 > MAX_RANGE_DAYS:
        raise InsightsRangeTooLongError
    return DayRange(first_day=resolved_first_day, last_day=resolved_last_day)

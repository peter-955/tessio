from datetime import UTC, date, datetime, time

from app.modules.insights.domains.day_range.entity import DayRange
from app.modules.insights.typing.constants import ONE_DAY


def start_of_day(day: date) -> datetime:
    return datetime.combine(day, time.min, tzinfo=UTC)


def end_of_day(day: date) -> datetime:
    return start_of_day(day + ONE_DAY)


def resolve_range_bounds(day_range: DayRange) -> tuple[datetime, datetime]:
    return start_of_day(day_range.first_day), end_of_day(day_range.last_day)

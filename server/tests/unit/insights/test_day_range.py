from datetime import date

import pytest

from app.modules.insights.errors import InsightsRangeInvalidError, InsightsRangeTooLongError
from app.modules.insights.utils.day_range import resolve_day_range

TODAY = date(2026, 11, 2)


def test_the_default_range_is_the_last_thirty_days() -> None:
    day_range = resolve_day_range(None, None, TODAY)

    assert (day_range.first_day, day_range.last_day) == (date(2026, 10, 4), TODAY)
    assert len(day_range.days) == 30


def test_a_start_alone_runs_to_today() -> None:
    day_range = resolve_day_range(date(2026, 10, 20), None, TODAY)

    assert (day_range.first_day, day_range.last_day) == (date(2026, 10, 20), TODAY)


def test_an_end_alone_covers_the_thirty_days_before_it() -> None:
    day_range = resolve_day_range(None, date(2026, 10, 30), TODAY)

    assert day_range.first_day == date(2026, 10, 1)


def test_a_reversed_or_too_long_range_is_refused() -> None:
    with pytest.raises(InsightsRangeInvalidError):
        resolve_day_range(date(2026, 10, 5), date(2026, 10, 1), TODAY)
    with pytest.raises(InsightsRangeTooLongError):
        resolve_day_range(date(2025, 1, 1), date(2026, 1, 2), TODAY)
    assert len(resolve_day_range(date(2025, 1, 2), date(2026, 1, 2), TODAY).days) == 366

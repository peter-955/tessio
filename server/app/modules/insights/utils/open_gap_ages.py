from collections.abc import Iterable, Sequence
from datetime import date
from statistics import median

from app.modules.insights.domains.gap_span.entity import GapSpan
from app.modules.insights.utils.day_bounds import end_of_day


def count_open_gaps_by_day(gap_spans: Sequence[GapSpan], days: Iterable[date]) -> dict[date, tuple[int, int | None]]:
    open_gaps: dict[date, tuple[int, int | None]] = {}
    for day in days:
        moment = end_of_day(day)
        ages = [(moment - span.created_at).total_seconds() for span in gap_spans if span.is_open_at(moment)]
        open_gaps[day] = (len(ages), round(median(ages)) if ages else None)
    return open_gaps

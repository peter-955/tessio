from datetime import UTC, date, datetime, timedelta

from app.modules.insights.domains.gap_span.entity import GapSpan
from app.modules.insights.utils.open_gap_ages import count_open_gaps_by_day

MIDNIGHT = datetime(2026, 10, 2, tzinfo=UTC)
HOUR = timedelta(hours=1)


def test_open_gaps_are_counted_at_the_end_of_each_day_with_their_median_age() -> None:
    spans = [
        GapSpan(created_at=MIDNIGHT - 10 * HOUR, answered_at=None, reopened_at=None, is_open=True),
        GapSpan(created_at=MIDNIGHT - 4 * HOUR, answered_at=MIDNIGHT + 2 * HOUR, reopened_at=None, is_open=False),
        GapSpan(created_at=MIDNIGHT - 2 * HOUR, answered_at=MIDNIGHT - HOUR, reopened_at=None, is_open=False),
        GapSpan(created_at=MIDNIGHT + HOUR, answered_at=None, reopened_at=None, is_open=True),
    ]

    counts = count_open_gaps_by_day(spans, [date(2026, 10, 1), date(2026, 10, 2)])

    assert counts[date(2026, 10, 1)] == (2, 7 * 3600)
    assert counts[date(2026, 10, 2)] == (2, round(28.5 * 3600))


def test_a_reopened_gap_counts_again_after_it_was_reopened() -> None:
    span = GapSpan(
        created_at=MIDNIGHT - 30 * HOUR, answered_at=MIDNIGHT - 20 * HOUR, reopened_at=MIDNIGHT + HOUR, is_open=True
    )

    counts = count_open_gaps_by_day([span], [date(2026, 10, 1), date(2026, 10, 2)])

    assert counts[date(2026, 10, 1)] == (0, None)
    assert counts[date(2026, 10, 2)] == (1, 54 * 3600)

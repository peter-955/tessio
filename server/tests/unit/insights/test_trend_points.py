from datetime import UTC, date, datetime
from uuid import uuid7

from app.modules.insights.domains.daily_stats.entity import DailyStats
from app.modules.insights.domains.day_range.entity import DayRange
from app.modules.insights.domains.sprint_reference.entity import SprintReference
from app.modules.insights.utils.trend_points import (
    assign_days_to_sprints,
    build_empty_stats,
    build_sprint_points,
    build_trend_point,
    compute_pass_rate,
    list_executors,
)
from app.modules.stories import SprintState

PROJECT_ID = uuid7()


def build_stats(day: date, **values: object) -> DailyStats:
    return build_empty_stats(PROJECT_ID, day).model_copy(update=values)


def build_sprint(name: str, start: date, end: date | None) -> SprintReference:
    return SprintReference(
        id=uuid7(),
        name=name,
        state=SprintState.CLOSED,
        start_at=datetime(start.year, start.month, start.day, 8, tzinfo=UTC),
        end_at=None if end is None else datetime(end.year, end.month, end.day, 17, tzinfo=UTC),
    )


def test_the_pass_rate_leaves_skipped_results_out() -> None:
    assert compute_pass_rate(3, 1, 0) == 0.75
    assert compute_pass_rate(0, 0, 0) is None
    assert compute_pass_rate(1, 1, 1) == 0.3333


def test_executors_follow_the_fixed_order_then_the_alphabet() -> None:
    stats = [
        build_stats(date(2026, 10, 1), runs_by_executor={"manual": 1, "zeta": 2}),
        build_stats(date(2026, 10, 2), runs_by_executor={"ci": 1, "claude": 3, "alpha": 1, "script": 0}),
    ]

    assert list_executors(stats) == ["claude", "manual", "ci", "alpha", "zeta"]


def test_a_period_sums_counts_and_keeps_the_last_open_gap_state() -> None:
    stats = [
        build_stats(
            date(2026, 10, 2),
            passed_count=2,
            failures_fixed=1,
            fix_seconds_total=100,
            open_gap_count=3,
            median_open_gap_age_seconds=50,
        ),
        build_stats(
            date(2026, 10, 1),
            failed_count=2,
            failures_fixed=1,
            fix_seconds_total=301,
            gaps_answered=2,
            answer_seconds_total=10,
            open_gap_count=9,
            median_open_gap_age_seconds=900,
        ),
    ]

    point = build_trend_point(stats, ["claude"], date(2026, 10, 1), date(2026, 10, 2))

    assert (point.passed_count, point.failed_count, point.pass_rate) == (2, 2, 0.5)
    assert point.mean_time_to_fix_seconds == 200
    assert point.mean_gap_answer_seconds == 5
    assert (point.open_gap_count, point.median_open_gap_age_seconds) == (3, 50)
    assert [(count.executor, count.count) for count in point.runs_by_executor] == [("claude", 0)]


def test_an_empty_period_has_no_rates() -> None:
    point = build_trend_point([], [], date(2026, 10, 1), date(2026, 10, 1))

    assert (point.run_count, point.pass_rate, point.mean_time_to_fix_seconds) == (0, None, None)
    assert (point.open_gap_count, point.median_open_gap_age_seconds) == (0, None)


def test_a_day_belongs_to_the_latest_started_sprint_and_open_sprints_reach_the_range_end() -> None:
    day_range = DayRange(first_day=date(2026, 10, 1), last_day=date(2026, 10, 10))
    first = build_sprint("First", date(2026, 9, 25), date(2026, 10, 4))
    overlapping = build_sprint("Overlapping", date(2026, 10, 3), date(2026, 10, 6))
    open_sprint = build_sprint("Open", date(2026, 10, 8), None)
    unstarted = SprintReference(id=uuid7(), name="Later", state=SprintState.FUTURE, start_at=None, end_at=None)

    assigned = assign_days_to_sprints([open_sprint, unstarted, overlapping, first], day_range)

    assert [(sprint.name, days[0].day, days[-1].day) for sprint, days in assigned] == [
        ("First", 1, 2),
        ("Overlapping", 3, 6),
        ("Open", 8, 10),
    ]


def test_sprint_points_use_only_the_days_of_each_sprint() -> None:
    day_range = DayRange(first_day=date(2026, 10, 1), last_day=date(2026, 10, 3))
    sprint = build_sprint("Only", date(2026, 10, 2), date(2026, 10, 3))
    stats = [build_stats(day, passed_count=1) for day in day_range.days]

    (point,) = build_sprint_points(stats, [sprint], day_range, [])

    assert point.sprint == sprint
    assert (point.first_day, point.last_day, point.passed_count) == (date(2026, 10, 2), date(2026, 10, 3), 2)

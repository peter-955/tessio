from collections.abc import Sequence
from datetime import date
from uuid import UUID

from app.modules.insights.domains.daily_stats.entity import DailyStats
from app.modules.insights.domains.day_range.entity import DayRange
from app.modules.insights.domains.executor_count.entity import ExecutorCount
from app.modules.insights.domains.sprint_reference.entity import SprintReference
from app.modules.insights.domains.trend_point.entity import TrendPoint
from app.modules.insights.typing.constants import EXECUTOR_ORDER, PASS_RATE_DIGITS


def build_empty_stats(project_id: UUID, day: date) -> DailyStats:
    return DailyStats(
        project_id=project_id,
        day=day,
        runs_by_executor={},
        passed_count=0,
        failed_count=0,
        blocked_count=0,
        skipped_count=0,
        failures_opened=0,
        failures_fixed=0,
        fix_seconds_total=0,
        gaps_opened=0,
        gaps_answered=0,
        answer_seconds_total=0,
        open_gap_count=0,
        median_open_gap_age_seconds=None,
    )


def list_executors(stats: Sequence[DailyStats]) -> list[str]:
    seen = {executor for day_stats in stats for executor, count in day_stats.runs_by_executor.items() if count}
    known = [executor for executor in EXECUTOR_ORDER if executor in seen]
    return known + sorted(seen - set(EXECUTOR_ORDER))


def compute_pass_rate(passed_count: int, failed_count: int, blocked_count: int) -> float | None:
    decided_count = passed_count + failed_count + blocked_count
    return None if decided_count == 0 else round(passed_count / decided_count, PASS_RATE_DIGITS)


def compute_mean(total: int, count: int) -> int | None:
    return None if count == 0 else round(total / count)


def build_trend_point(
    stats: Sequence[DailyStats],
    executors: Sequence[str],
    first_day: date,
    last_day: date,
    day: date | None = None,
    sprint: SprintReference | None = None,
) -> TrendPoint:
    ordered = sorted(stats, key=lambda day_stats: day_stats.day)
    passed_count = sum(day_stats.passed_count for day_stats in ordered)
    failed_count = sum(day_stats.failed_count for day_stats in ordered)
    blocked_count = sum(day_stats.blocked_count for day_stats in ordered)
    failures_fixed = sum(day_stats.failures_fixed for day_stats in ordered)
    gaps_answered = sum(day_stats.gaps_answered for day_stats in ordered)
    runs_by_executor = [
        ExecutorCount(
            executor=executor,
            count=sum(day_stats.runs_by_executor.get(executor, 0) for day_stats in ordered),
        )
        for executor in executors
    ]
    last_stats = ordered[-1] if ordered else None
    return TrendPoint(
        day=day,
        sprint=sprint,
        first_day=first_day,
        last_day=last_day,
        run_count=sum(sum(day_stats.runs_by_executor.values()) for day_stats in ordered),
        runs_by_executor=runs_by_executor,
        passed_count=passed_count,
        failed_count=failed_count,
        blocked_count=blocked_count,
        skipped_count=sum(day_stats.skipped_count for day_stats in ordered),
        pass_rate=compute_pass_rate(passed_count, failed_count, blocked_count),
        failures_opened=sum(day_stats.failures_opened for day_stats in ordered),
        failures_fixed=failures_fixed,
        mean_time_to_fix_seconds=compute_mean(
            sum(day_stats.fix_seconds_total for day_stats in ordered), failures_fixed
        ),
        gaps_opened=sum(day_stats.gaps_opened for day_stats in ordered),
        gaps_answered=gaps_answered,
        mean_gap_answer_seconds=compute_mean(
            sum(day_stats.answer_seconds_total for day_stats in ordered), gaps_answered
        ),
        open_gap_count=0 if last_stats is None else last_stats.open_gap_count,
        median_open_gap_age_seconds=None if last_stats is None else last_stats.median_open_gap_age_seconds,
    )


def build_day_points(stats: Sequence[DailyStats], executors: Sequence[str]) -> list[TrendPoint]:
    return [
        build_trend_point([day_stats], executors, day_stats.day, day_stats.day, day=day_stats.day)
        for day_stats in sorted(stats, key=lambda day_stats: day_stats.day)
    ]


def assign_days_to_sprints(
    sprints: Sequence[SprintReference], day_range: DayRange
) -> list[tuple[SprintReference, list[date]]]:
    started_sprints = sorted(
        (sprint for sprint in sprints if sprint.start_at is not None),
        key=lambda sprint: (sprint.start_at, sprint.id),
    )
    days_by_sprint: dict[UUID, list[date]] = {sprint.id: [] for sprint in started_sprints}
    for day in day_range.days:
        owner: SprintReference | None = None
        for sprint in started_sprints:
            if sprint.start_at is None:
                continue
            sprint_last_day = day_range.last_day if sprint.end_at is None else sprint.end_at.date()
            if sprint.start_at.date() <= day <= sprint_last_day:
                owner = sprint
        if owner is not None:
            days_by_sprint[owner.id].append(day)
    return [(sprint, days_by_sprint[sprint.id]) for sprint in started_sprints if days_by_sprint[sprint.id]]


def build_sprint_points(
    stats: Sequence[DailyStats],
    sprints: Sequence[SprintReference],
    day_range: DayRange,
    executors: Sequence[str],
) -> list[TrendPoint]:
    stats_by_day = {day_stats.day: day_stats for day_stats in stats}
    points: list[TrendPoint] = []
    for sprint, days in assign_days_to_sprints(sprints, day_range):
        sprint_stats = [stats_by_day[day] for day in days if day in stats_by_day]
        points.append(build_trend_point(sprint_stats, executors, days[0], days[-1], sprint=sprint))
    return points

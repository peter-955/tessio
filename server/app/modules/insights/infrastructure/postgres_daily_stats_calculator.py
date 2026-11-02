from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID

from sqlalchemy import Text, func, or_, select, type_coerce

from app.modules.failures.infrastructure import FailureEventTable, FailureTable
from app.modules.failures.typing.enums import FailureEventKind, FailureStatus
from app.modules.gaps.infrastructure import GapTable
from app.modules.gaps.typing.enums import GapStatus
from app.modules.insights.domains.daily_stats.entity import DailyStats
from app.modules.insights.domains.day_range.entity import DayRange
from app.modules.insights.domains.gap_span.entity import GapSpan
from app.modules.insights.domains.insights_project.entity import InsightsProject
from app.modules.insights.infrastructure.utc_day import utc_day
from app.modules.insights.ports.daily_stats_calculator import DailyStatsCalculator
from app.modules.insights.utils.day_bounds import resolve_range_bounds
from app.modules.insights.utils.open_gap_ages import count_open_gaps_by_day
from app.modules.projects.infrastructure import ProjectTable
from app.modules.runs import ResultStatus
from app.modules.runs.infrastructure import CaseResultTable, RunTable, is_worst_iteration
from app.shared.postgres import Database

STAT_DAY = "stat_day"
FIXED_STATUSES = (FailureStatus.FIXED, FailureStatus.VERIFIED)


def to_seconds(value: Decimal | float | None) -> int:
    return 0 if value is None else round(value)


class PostgresDailyStatsCalculator(DailyStatsCalculator):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_snapshot_projects(self) -> list[InsightsProject]:
        result = await self._database.get_current_session().execute(
            select(ProjectTable.id, ProjectTable.created_at)
            .where(ProjectTable.archived_at.is_(None))
            .order_by(ProjectTable.created_at, ProjectTable.id)
        )
        return [InsightsProject(id=project_id, created_at=created_at) for project_id, created_at in result]

    async def compute(self, project_id: UUID, day_range: DayRange) -> list[DailyStats]:
        start_at, end_at = resolve_range_bounds(day_range)
        runs = await self._count_runs(project_id, start_at, end_at)
        results = await self._count_results(project_id, start_at, end_at)
        failures_opened = await self._count_failures_opened(project_id, start_at, end_at)
        failures_fixed = await self._count_failures_fixed(project_id, start_at, end_at)
        gaps_opened = await self._count_gaps_opened(project_id, start_at, end_at)
        gaps_answered = await self._count_gaps_answered(project_id, start_at, end_at)
        open_gaps = count_open_gaps_by_day(await self._list_gap_spans(project_id, start_at, end_at), day_range.days)
        stats: list[DailyStats] = []
        for day in day_range.days:
            day_results = results.get(day, {})
            fixed_count, fix_seconds = failures_fixed.get(day, (0, 0))
            answered_count, answer_seconds = gaps_answered.get(day, (0, 0))
            open_gap_count, median_age = open_gaps[day]
            stats.append(
                DailyStats(
                    project_id=project_id,
                    day=day,
                    runs_by_executor=runs.get(day, {}),
                    passed_count=day_results.get(ResultStatus.PASSED, 0),
                    failed_count=day_results.get(ResultStatus.FAILED, 0),
                    blocked_count=day_results.get(ResultStatus.BLOCKED, 0),
                    skipped_count=day_results.get(ResultStatus.SKIPPED, 0),
                    failures_opened=failures_opened.get(day, 0),
                    failures_fixed=fixed_count,
                    fix_seconds_total=fix_seconds,
                    gaps_opened=gaps_opened.get(day, 0),
                    gaps_answered=answered_count,
                    answer_seconds_total=answer_seconds,
                    open_gap_count=open_gap_count,
                    median_open_gap_age_seconds=median_age,
                )
            )
        return stats

    async def _count_runs(self, project_id: UUID, start_at: datetime, end_at: datetime) -> dict[date, dict[str, int]]:
        executor = type_coerce(RunTable.executor, Text)
        result = await self._database.get_current_session().execute(
            select(utc_day(RunTable.started_at).label(STAT_DAY), executor, func.count(RunTable.id))
            .where(RunTable.project_id == project_id, RunTable.started_at >= start_at, RunTable.started_at < end_at)
            .group_by(STAT_DAY, executor)
        )
        counts: defaultdict[date, dict[str, int]] = defaultdict(dict)
        for day, executor_value, count in result:
            counts[day][str(executor_value)] = count
        return dict(counts)

    async def _count_results(
        self, project_id: UUID, start_at: datetime, end_at: datetime
    ) -> dict[date, dict[ResultStatus, int]]:
        result = await self._database.get_current_session().execute(
            select(utc_day(CaseResultTable.created_at).label(STAT_DAY), CaseResultTable.status, func.count())
            .join(RunTable, RunTable.id == CaseResultTable.run_id)
            .where(
                RunTable.project_id == project_id,
                CaseResultTable.created_at >= start_at,
                CaseResultTable.created_at < end_at,
                is_worst_iteration(),
            )
            .group_by(STAT_DAY, CaseResultTable.status)
        )
        counts: defaultdict[date, dict[ResultStatus, int]] = defaultdict(dict)
        for day, status, count in result:
            counts[day][ResultStatus(status)] = count
        return dict(counts)

    async def _count_failures_opened(self, project_id: UUID, start_at: datetime, end_at: datetime) -> dict[date, int]:
        result = await self._database.get_current_session().execute(
            select(utc_day(FailureTable.created_at).label(STAT_DAY), func.count(FailureTable.id))
            .where(
                FailureTable.project_id == project_id,
                FailureTable.created_at >= start_at,
                FailureTable.created_at < end_at,
            )
            .group_by(STAT_DAY)
        )
        return dict(result.all())

    async def _count_failures_fixed(
        self, project_id: UUID, start_at: datetime, end_at: datetime
    ) -> dict[date, tuple[int, int]]:
        first_fixes = (
            select(
                FailureEventTable.failure_id.label("failure_id"),
                func.min(FailureEventTable.created_at).label("fixed_at"),
            )
            .join(FailureTable, FailureTable.id == FailureEventTable.failure_id)
            .where(
                FailureTable.project_id == project_id,
                FailureEventTable.kind == FailureEventKind.STATUS_CHANGED,
                FailureEventTable.to_status.in_(FIXED_STATUSES),
            )
            .group_by(FailureEventTable.failure_id)
            .subquery("first_fixes")
        )
        result = await self._database.get_current_session().execute(
            select(
                utc_day(first_fixes.c.fixed_at).label(STAT_DAY),
                func.count(),
                func.sum(func.extract("epoch", first_fixes.c.fixed_at - FailureTable.created_at)),
            )
            .join(FailureTable, FailureTable.id == first_fixes.c.failure_id)
            .where(first_fixes.c.fixed_at >= start_at, first_fixes.c.fixed_at < end_at)
            .group_by(STAT_DAY)
        )
        return {day: (count, to_seconds(seconds)) for day, count, seconds in result}

    async def _count_gaps_opened(self, project_id: UUID, start_at: datetime, end_at: datetime) -> dict[date, int]:
        result = await self._database.get_current_session().execute(
            select(utc_day(GapTable.created_at).label(STAT_DAY), func.count(GapTable.id))
            .where(GapTable.project_id == project_id, GapTable.created_at >= start_at, GapTable.created_at < end_at)
            .group_by(STAT_DAY)
        )
        return dict(result.all())

    async def _count_gaps_answered(
        self, project_id: UUID, start_at: datetime, end_at: datetime
    ) -> dict[date, tuple[int, int]]:
        answered_at = GapTable.answered_at
        result = await self._database.get_current_session().execute(
            select(
                utc_day(answered_at).label(STAT_DAY),
                func.count(GapTable.id),
                func.sum(func.extract("epoch", answered_at - GapTable.created_at)),
            )
            .where(GapTable.project_id == project_id, answered_at >= start_at, answered_at < end_at)
            .group_by(STAT_DAY)
        )
        return {day: (count, to_seconds(seconds)) for day, count, seconds in result}

    async def _list_gap_spans(self, project_id: UUID, start_at: datetime, end_at: datetime) -> list[GapSpan]:
        result = await self._database.get_current_session().execute(
            select(GapTable.created_at, GapTable.answered_at, GapTable.reopened_at, GapTable.status).where(
                GapTable.project_id == project_id,
                GapTable.created_at < end_at,
                or_(
                    GapTable.answered_at.is_(None),
                    GapTable.answered_at >= start_at,
                    GapTable.reopened_at.is_not(None),
                ),
            )
        )
        return [
            GapSpan(
                created_at=created_at,
                answered_at=answered_at,
                reopened_at=reopened_at,
                is_open=status == GapStatus.OPEN,
            )
            for created_at, answered_at, reopened_at, status in result
        ]

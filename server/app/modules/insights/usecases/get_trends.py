from datetime import UTC, date, datetime
from uuid import UUID

from app.modules.insights.domains.daily_stats.entity import DailyStats
from app.modules.insights.domains.daily_stats.repository import DailyStatsRepository
from app.modules.insights.domains.day_range.entity import DayRange
from app.modules.insights.domains.trends.entity import Trends
from app.modules.insights.ports.daily_stats_calculator import DailyStatsCalculator
from app.modules.insights.ports.story_scope_reader import StoryScopeReader
from app.modules.insights.typing.constants import MAX_SPRINT_COVERAGE_COUNT
from app.modules.insights.typing.enums import TrendGrouping
from app.modules.insights.utils.day_bounds import resolve_range_bounds
from app.modules.insights.utils.day_range import resolve_day_range
from app.modules.insights.utils.trend_points import (
    build_day_points,
    build_sprint_points,
    build_trend_point,
    list_executors,
)
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetTrendsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        daily_stats_repository: DailyStatsRepository,
        daily_stats_calculator: DailyStatsCalculator,
        story_scope_reader: StoryScopeReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._daily_stats_repository = daily_stats_repository
        self._daily_stats_calculator = daily_stats_calculator
        self._story_scope_reader = story_scope_reader

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        first_day: date | None,
        last_day: date | None,
        grouping: TrendGrouping,
    ) -> Trends:
        today = datetime.now(UTC).date()
        day_range = resolve_day_range(first_day, last_day, today)
        data_range = (
            None
            if day_range.first_day > today
            else DayRange(first_day=day_range.first_day, last_day=min(day_range.last_day, today))
        )
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            stats = [] if data_range is None else await self._load_stats(access.project_id, data_range, today)
            sprints = (
                []
                if grouping is TrendGrouping.DAY or data_range is None
                else await self._story_scope_reader.list_sprints_overlapping(
                    access.project_id, *resolve_range_bounds(data_range), MAX_SPRINT_COVERAGE_COUNT
                )
            )
        executors = list_executors(stats)
        points = (
            build_day_points(stats, executors)
            if grouping is TrendGrouping.DAY or data_range is None
            else build_sprint_points(stats, sprints, data_range, executors)
        )
        return Trends(
            grouping=grouping,
            day_range=day_range,
            executors=executors,
            points=points,
            total=build_trend_point(stats, executors, day_range.first_day, day_range.last_day),
        )

    async def _load_stats(self, project_id: UUID, data_range: DayRange, today: date) -> list[DailyStats]:
        stored = await self._daily_stats_repository.list_between(project_id, data_range.first_day, data_range.last_day)
        stats_by_day = {day_stats.day: day_stats for day_stats in stored if day_stats.day < today}
        missing_days = [day for day in data_range.days if day not in stats_by_day]
        if missing_days:
            computed = await self._daily_stats_calculator.compute(
                project_id, DayRange(first_day=missing_days[0], last_day=missing_days[-1])
            )
            stats_by_day.update({day_stats.day: day_stats for day_stats in computed if day_stats.day in missing_days})
        return [stats_by_day[day] for day in data_range.days]

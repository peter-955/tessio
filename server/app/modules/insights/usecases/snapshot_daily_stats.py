from datetime import UTC, date, datetime, timedelta

from app.modules.insights.domains.daily_stats.repository import DailyStatsRepository
from app.modules.insights.domains.day_range.entity import DayRange
from app.modules.insights.domains.insights_project.entity import InsightsProject
from app.modules.insights.ports.daily_stats_calculator import DailyStatsCalculator
from app.modules.insights.typing.constants import ONE_DAY, SNAPSHOT_BACKFILL_DAYS
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType


class SnapshotDailyStatsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        daily_stats_calculator: DailyStatsCalculator,
        daily_stats_repository: DailyStatsRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._daily_stats_calculator = daily_stats_calculator
        self._daily_stats_repository = daily_stats_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, today: date) -> int:
        async with self._transaction.begin():
            projects = await self._daily_stats_calculator.list_snapshot_projects()
        snapshot_count = 0
        for project in projects:
            if await self._snapshot_project(project, today - ONE_DAY):
                snapshot_count += 1
                await self._live_event_publisher.publish(
                    LiveEvent(type=LiveEventType.INSIGHTS_CHANGED, project_id=project.id)
                )
        return snapshot_count

    async def _snapshot_project(self, project: InsightsProject, last_day: date) -> bool:
        first_day = max(
            project.created_at.astimezone(UTC).date(), last_day - timedelta(days=SNAPSHOT_BACKFILL_DAYS - 1)
        )
        if first_day > last_day:
            return False
        window = DayRange(first_day=first_day, last_day=last_day)
        async with self._transaction.begin():
            stored = await self._daily_stats_repository.list_between(project.id, first_day, last_day)
            recorded_days = {day_stats.day for day_stats in stored if day_stats.day != last_day}
            missing_days = [day for day in window.days if day not in recorded_days]
            computed = await self._daily_stats_calculator.compute(
                project.id, DayRange(first_day=missing_days[0], last_day=last_day)
            )
            await self._daily_stats_repository.save_all(
                [day_stats for day_stats in computed if day_stats.day not in recorded_days], datetime.now(UTC)
            )
        return True

from datetime import UTC, datetime

from pydantic import JsonValue

from app.modules.insights.usecases.snapshot_daily_stats import SnapshotDailyStatsUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class DailySnapshotJobHandler(JobHandler):
    def __init__(self, use_case: SnapshotDailyStatsUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        project_count = await self._use_case.execute(datetime.now(UTC).date())
        log.info("insights.daily_snapshot_written", extra={"count": project_count})

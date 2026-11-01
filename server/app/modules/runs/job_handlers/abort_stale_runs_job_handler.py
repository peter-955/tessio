from datetime import UTC, datetime

from pydantic import JsonValue

from app.modules.runs.usecases.abort_stale_runs import AbortStaleRunsUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class AbortStaleRunsJobHandler(JobHandler):
    def __init__(self, use_case: AbortStaleRunsUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        aborted_count = await self._use_case.execute(datetime.now(UTC))
        log.info("runs.stale_aborted", extra={"count": aborted_count})

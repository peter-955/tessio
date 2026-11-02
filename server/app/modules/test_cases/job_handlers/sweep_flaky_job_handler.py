from pydantic import JsonValue

from app.modules.test_cases.usecases.sweep_flaky import SweepFlakyUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class SweepFlakyJobHandler(JobHandler):
    def __init__(self, use_case: SweepFlakyUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        case_count = await self._use_case.execute()
        log.info("test_cases.flaky_swept", extra={"count": case_count})

from uuid import UUID

from pydantic import JsonValue

from app.modules.test_cases.typing.constants.flaky_case import FLAKY_JOB_CASE_ID_KEY
from app.modules.test_cases.usecases.recompute_flaky import RecomputeFlakyUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class RecomputeFlakyJobHandler(JobHandler):
    def __init__(self, use_case: RecomputeFlakyUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        test_case_id_value = data.get(FLAKY_JOB_CASE_ID_KEY)
        try:
            test_case_id = UUID(test_case_id_value) if isinstance(test_case_id_value, str) else None
        except ValueError:
            test_case_id = None
        if test_case_id is None:
            log.warning("test_cases.flaky_invalid_job_data", extra={"test_case_id": str(test_case_id_value)})
            return
        await self._use_case.execute(test_case_id)

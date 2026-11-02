from uuid import UUID

from redis.exceptions import RedisError

from app.modules.runs.ports.flaky_recompute_requester import FlakyRecomputeRequester
from app.modules.test_cases import build_recompute_flaky_job_data
from app.shared.logging import get_logger
from app.shared.queue import JobQueue
from app.shared.typing.enums import JobName, QueueName

log = get_logger(__name__)


class QueuedFlakyRecomputeRequester(FlakyRecomputeRequester):
    def __init__(self, job_queue: JobQueue) -> None:
        self._job_queue = job_queue

    async def request(self, test_case_id: UUID) -> None:
        try:
            await self._job_queue.add(
                QueueName.MAINTENANCE,
                JobName.TEST_CASES_RECOMPUTE_FLAKY,
                build_recompute_flaky_job_data(test_case_id),
            )
        except RedisError as error:
            log.warning(
                "test_cases.flaky_enqueue_failed",
                extra={"test_case_id": str(test_case_id), "reason": type(error).__name__},
            )

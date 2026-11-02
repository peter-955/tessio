import asyncio
from uuid import UUID, uuid7

from app.modules.runs.infrastructure import QueuedFlakyRecomputeRequester
from app.modules.test_cases import RecomputeFlakyJobHandler, RecomputeFlakyUseCase
from app.shared.queue import BullmqJobQueue, BullmqJobWorker
from app.shared.typing.enums import JobName, QueueName

WORKER_TIMEOUT_SECONDS = 10


class SignallingRecomputeFlaky(RecomputeFlakyUseCase):
    def __init__(self) -> None:
        self.test_case_ids: list[UUID] = []
        self.received = asyncio.Event()

    async def execute(self, test_case_id: UUID) -> None:
        self.test_case_ids.append(test_case_id)
        self.received.set()


async def test_a_requested_recompute_is_run_by_the_maintenance_worker(redis_url: str) -> None:
    recompute = SignallingRecomputeFlaky()
    test_case_id = uuid7()
    job_queue = BullmqJobQueue(redis_url)
    job_worker = BullmqJobWorker(
        redis_url, QueueName.MAINTENANCE, {JobName.TEST_CASES_RECOMPUTE_FLAKY: RecomputeFlakyJobHandler(recompute)}
    )
    job_worker.start()
    try:
        await QueuedFlakyRecomputeRequester(job_queue).request(test_case_id)
        await asyncio.wait_for(recompute.received.wait(), WORKER_TIMEOUT_SECONDS)
    finally:
        await job_worker.close()
        await job_queue.close()

    assert recompute.test_case_ids == [test_case_id]

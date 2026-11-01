import asyncio
import uuid

from pydantic import JsonValue

from app.shared.queue import BullmqJobQueue, JobHandler, build_job_workers
from app.shared.typing.enums import JobName, QueueName

WORKER_TIMEOUT_SECONDS = 10


class SignallingJobHandler(JobHandler):
    def __init__(self) -> None:
        self.received_data: list[dict[str, JsonValue]] = []
        self.received = asyncio.Event()

    async def handle(self, data: dict[str, JsonValue]) -> None:
        self.received_data.append(data)
        self.received.set()


def test_one_worker_is_built_per_queue(redis_url: str) -> None:
    job_workers = build_job_workers(redis_url, {QueueName.EMAIL: {}})

    assert [job_worker.queue_name for job_worker in job_workers] == list(QueueName)


async def test_maintenance_job_is_handled_by_its_worker(redis_url: str) -> None:
    handler = SignallingJobHandler()
    marker = uuid.uuid4().hex
    job_workers = build_job_workers(redis_url, {QueueName.MAINTENANCE: {JobName.SESSIONS_DELETE_EXPIRED: handler}})
    job_queue = BullmqJobQueue(redis_url)
    for job_worker in job_workers:
        job_worker.start()
    try:
        await job_queue.add(QueueName.MAINTENANCE, JobName.SESSIONS_DELETE_EXPIRED, {"marker": marker})
        await asyncio.wait_for(handler.received.wait(), WORKER_TIMEOUT_SECONDS)
    finally:
        await asyncio.gather(*(job_worker.close() for job_worker in job_workers))
        await job_queue.close()

    assert handler.received_data == [{"marker": marker}]

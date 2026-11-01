import asyncio
import os
import signal
import uuid

import pytest
from bullmq import Queue

from app.config import Settings
from app.shared.queue import BullmqJobQueue, BullmqJobWorker, JobSchedule
from app.shared.typing.enums import JobName, QueueName
from app.workers import worker
from tests.support.test_settings import build_test_settings

WORKER_TIMEOUT_SECONDS = 10
WORKER_SETTLE_SECONDS = 0.5


class RecordingJobWorker(BullmqJobWorker):
    def __init__(self, redis_url: str, queue_name: QueueName, started: asyncio.Event) -> None:
        super().__init__(redis_url, queue_name, {})
        self._started = started
        self.is_running = False

    def start(self) -> None:
        super().start()
        self.is_running = True
        self._started.set()

    async def close(self) -> None:
        await super().close()
        self.is_running = False


class WorkerTestContainer:
    def __init__(self, redis_url: str, schedules: tuple[JobSchedule, ...]) -> None:
        self.started_events = {queue_name: asyncio.Event() for queue_name in QueueName}
        self.job_queue = BullmqJobQueue(redis_url)
        self.job_schedules = schedules
        self.job_workers = [
            RecordingJobWorker(redis_url, queue_name, self.started_events[queue_name]) for queue_name in QueueName
        ]
        self.is_closed = False

    async def close(self) -> None:
        await self.job_queue.close()
        self.is_closed = True


async def test_worker_schedules_jobs_and_stops_every_queue_worker_on_sigterm(
    redis_url: str, database_url: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    schedule = JobSchedule(
        scheduler_id=f"sessions.delete_expired-{uuid.uuid4().hex[:8]}",
        queue_name=QueueName.MAINTENANCE,
        job_name=JobName.SESSIONS_DELETE_EXPIRED,
        cron_pattern="30 3 * * *",
    )
    test_container = WorkerTestContainer(redis_url, (schedule,))
    settings = build_test_settings(database_url, redis_url)

    def build_container(_: Settings) -> WorkerTestContainer:
        return test_container

    monkeypatch.setattr(worker, "Container", build_container)
    monkeypatch.setattr(worker, "get_settings", lambda: settings)
    maintenance_queue = Queue(QueueName.MAINTENANCE.value, {"connection": redis_url})
    worker_task = asyncio.create_task(worker.run_worker())
    try:
        await asyncio.wait_for(
            asyncio.gather(*(event.wait() for event in test_container.started_events.values())),
            WORKER_TIMEOUT_SECONDS,
        )
        scheduler = await maintenance_queue.getJobScheduler(schedule.scheduler_id)
        await asyncio.sleep(WORKER_SETTLE_SECONDS)
        os.kill(os.getpid(), signal.SIGTERM)
        await asyncio.wait_for(worker_task, WORKER_TIMEOUT_SECONDS)
    finally:
        cleanup_queue = BullmqJobQueue(redis_url)
        await cleanup_queue.replace_schedules([])
        await cleanup_queue.close()
        await maintenance_queue.drain(True)
        await maintenance_queue.close()

    assert scheduler["name"] == JobName.SESSIONS_DELETE_EXPIRED.value
    assert [job_worker.queue_name for job_worker in test_container.job_workers] == list(QueueName)
    assert not any(job_worker.is_running for job_worker in test_container.job_workers)
    assert test_container.is_closed

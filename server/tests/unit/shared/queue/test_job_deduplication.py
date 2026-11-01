import uuid
from collections.abc import AsyncIterator

import pytest
from bullmq import Queue

from app.shared.queue import BullmqJobQueue
from app.shared.typing.enums import JobName, QueueName


@pytest.fixture
async def job_queue(redis_url: str) -> AsyncIterator[BullmqJobQueue]:
    bullmq_job_queue = BullmqJobQueue(redis_url)
    yield bullmq_job_queue
    await bullmq_job_queue.close()


@pytest.fixture
async def inspected_queue(redis_url: str) -> AsyncIterator[Queue]:
    queue = Queue(QueueName.JIRA.value, {"connection": redis_url})
    yield queue
    await queue.drain()
    await queue.close()


async def count_waiting_jobs(queue: Queue, marker: str) -> int:
    jobs = await queue.getJobs(["waiting"])
    return sum(1 for job in jobs if job.data.get("marker") == marker)


async def test_same_job_id_is_added_once(job_queue: BullmqJobQueue, inspected_queue: Queue) -> None:
    marker = uuid.uuid4().hex
    job_id = f"jira-sync-{uuid.uuid4()}"

    await job_queue.add(QueueName.JIRA, JobName.JIRA_SYNC_PROJECT, {"marker": marker}, job_id=job_id)
    await job_queue.add(QueueName.JIRA, JobName.JIRA_SYNC_PROJECT, {"marker": marker}, job_id=job_id)

    assert await count_waiting_jobs(inspected_queue, marker) == 1


async def test_different_job_ids_are_added_separately(job_queue: BullmqJobQueue, inspected_queue: Queue) -> None:
    marker = uuid.uuid4().hex

    await job_queue.add(
        QueueName.JIRA, JobName.JIRA_SYNC_PROJECT, {"marker": marker}, job_id=f"jira-sync-{uuid.uuid4()}"
    )
    await job_queue.add(
        QueueName.JIRA, JobName.JIRA_SYNC_PROJECT, {"marker": marker}, job_id=f"jira-sync-{uuid.uuid4()}"
    )

    assert await count_waiting_jobs(inspected_queue, marker) == 2


async def test_jobs_without_job_id_are_never_deduplicated(job_queue: BullmqJobQueue, inspected_queue: Queue) -> None:
    marker = uuid.uuid4().hex

    await job_queue.add(QueueName.JIRA, JobName.JIRA_SYNC_PROJECT, {"marker": marker})
    await job_queue.add(QueueName.JIRA, JobName.JIRA_SYNC_PROJECT, {"marker": marker})

    assert await count_waiting_jobs(inspected_queue, marker) == 2

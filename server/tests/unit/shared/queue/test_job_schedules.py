import uuid
from collections.abc import AsyncIterator

import pytest
from bullmq import Queue

from app.shared.queue import BullmqJobQueue, JobSchedule
from app.shared.typing.enums import JobName, QueueName


@pytest.fixture
async def job_queue(redis_url: str) -> AsyncIterator[BullmqJobQueue]:
    bullmq_job_queue = BullmqJobQueue(redis_url)
    yield bullmq_job_queue
    await bullmq_job_queue.replace_schedules([])
    await bullmq_job_queue.close()


@pytest.fixture
async def queues(redis_url: str) -> AsyncIterator[dict[QueueName, Queue]]:
    inspected_queues = {queue_name: Queue(queue_name.value, {"connection": redis_url}) for queue_name in QueueName}
    yield inspected_queues
    for queue in inspected_queues.values():
        await queue.drain(True)
        await queue.close()


def build_schedules() -> list[JobSchedule]:
    suffix = uuid.uuid4().hex[:8]
    return [
        JobSchedule(
            scheduler_id=f"files.delete_orphans-{suffix}",
            queue_name=QueueName.MAINTENANCE,
            job_name=JobName.FILES_DELETE_ORPHANS,
            cron_pattern="0 3 * * *",
        ),
        JobSchedule(
            scheduler_id=f"sessions.delete_expired-{suffix}",
            queue_name=QueueName.MAINTENANCE,
            job_name=JobName.SESSIONS_DELETE_EXPIRED,
            cron_pattern="30 3 * * *",
            timezone="Europe/Paris",
        ),
        JobSchedule(
            scheduler_id=f"jira.sync_project-{suffix}",
            queue_name=QueueName.JIRA,
            job_name=JobName.JIRA_SYNC_PROJECT,
            cron_pattern="*/15 * * * *",
        ),
    ]


async def list_scheduler_ids(queue: Queue) -> set[str]:
    return {scheduler["key"] for scheduler in await queue.getJobSchedulers()}


async def test_replacing_schedules_twice_keeps_one_scheduler_per_spec(
    job_queue: BullmqJobQueue, queues: dict[QueueName, Queue]
) -> None:
    schedules = build_schedules()

    await job_queue.replace_schedules(schedules)
    await job_queue.replace_schedules(schedules)

    assert await queues[QueueName.MAINTENANCE].getJobSchedulersCount() == 2
    assert await queues[QueueName.JIRA].getJobSchedulersCount() == 1
    assert await queues[QueueName.EMAIL].getJobSchedulersCount() == 0
    assert await list_scheduler_ids(queues[QueueName.MAINTENANCE]) == {
        schedules[0].scheduler_id,
        schedules[1].scheduler_id,
    }
    assert await queues[QueueName.MAINTENANCE].getJobCountByTypes("delayed") == 2


async def test_scheduler_keeps_its_pattern_and_timezone(
    job_queue: BullmqJobQueue, queues: dict[QueueName, Queue]
) -> None:
    schedules = build_schedules()

    await job_queue.replace_schedules(schedules)

    scheduler = await queues[QueueName.MAINTENANCE].getJobScheduler(schedules[1].scheduler_id)
    assert scheduler["name"] == JobName.SESSIONS_DELETE_EXPIRED.value
    assert scheduler["pattern"] == "30 3 * * *"
    assert scheduler["tz"] == "Europe/Paris"


async def test_removed_spec_is_unscheduled(job_queue: BullmqJobQueue, queues: dict[QueueName, Queue]) -> None:
    schedules = build_schedules()
    await job_queue.replace_schedules(schedules)

    await job_queue.replace_schedules(schedules[1:])

    assert await list_scheduler_ids(queues[QueueName.MAINTENANCE]) == {schedules[1].scheduler_id}
    assert await list_scheduler_ids(queues[QueueName.JIRA]) == {schedules[2].scheduler_id}

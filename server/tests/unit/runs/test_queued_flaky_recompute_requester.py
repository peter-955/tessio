from collections.abc import Sequence
from uuid import uuid7

from pydantic import JsonValue
from redis.exceptions import ConnectionError as RedisConnectionError

from app.modules.runs.infrastructure import QueuedFlakyRecomputeRequester
from app.shared.queue import JobQueue, JobSchedule
from app.shared.typing.enums import JobName, QueueName
from tests.support.recording_job_queue import RecordedJob, RecordingJobQueue


class UnreachableJobQueue(JobQueue):
    async def add(
        self, queue_name: QueueName, job_name: JobName, data: dict[str, JsonValue], job_id: str | None = None
    ) -> None:
        raise RedisConnectionError("Redis is down")

    async def replace_schedules(self, schedules: Sequence[JobSchedule]) -> None:
        return None

    async def close(self) -> None:
        return None


async def test_the_request_enqueues_one_recompute_job_for_the_case() -> None:
    job_queue = RecordingJobQueue()
    test_case_id = uuid7()

    await QueuedFlakyRecomputeRequester(job_queue).request(test_case_id)

    assert job_queue.jobs == [
        RecordedJob(
            queue_name=QueueName.MAINTENANCE,
            job_name=JobName.TEST_CASES_RECOMPUTE_FLAKY,
            data={"testCaseId": str(test_case_id)},
            job_id=None,
        )
    ]


async def test_an_unreachable_queue_does_not_fail_the_recorded_result() -> None:
    await QueuedFlakyRecomputeRequester(UnreachableJobQueue()).request(uuid7())

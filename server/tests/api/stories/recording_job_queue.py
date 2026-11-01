from collections.abc import Sequence
from dataclasses import dataclass

from pydantic import JsonValue

from app.shared.queue import JobQueue, JobSchedule
from app.shared.typing.enums import JobName, QueueName


@dataclass(frozen=True)
class RecordedJob:
    queue_name: QueueName
    job_name: JobName
    data: dict[str, JsonValue]
    job_id: str | None


class RecordingJobQueue(JobQueue):
    def __init__(self) -> None:
        self.jobs: list[RecordedJob] = []

    async def add(
        self, queue_name: QueueName, job_name: JobName, data: dict[str, JsonValue], job_id: str | None = None
    ) -> None:
        self.jobs.append(RecordedJob(queue_name=queue_name, job_name=job_name, data=data, job_id=job_id))

    async def replace_schedules(self, schedules: Sequence[JobSchedule]) -> None:
        return None

    async def close(self) -> None:
        return None

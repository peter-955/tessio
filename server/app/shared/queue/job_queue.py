from abc import ABC, abstractmethod
from collections.abc import Sequence

from pydantic import JsonValue

from app.shared.queue.job_schedule import JobSchedule
from app.shared.typing.enums import JobName, QueueName


class JobQueue(ABC):
    @abstractmethod
    async def add(
        self, queue_name: QueueName, job_name: JobName, data: dict[str, JsonValue], job_id: str | None = None
    ) -> None: ...

    @abstractmethod
    async def replace_schedules(self, schedules: Sequence[JobSchedule]) -> None: ...

    @abstractmethod
    async def close(self) -> None: ...

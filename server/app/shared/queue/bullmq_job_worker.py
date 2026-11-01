from collections.abc import Mapping

from bullmq import Job, UnrecoverableError, Worker

from app.shared.logging import get_logger
from app.shared.queue.job_handler import JobHandler
from app.shared.typing.enums import JobName, QueueName

log = get_logger(__name__)


class BullmqJobWorker:
    def __init__(self, redis_url: str, queue_name: QueueName, handlers: Mapping[JobName, JobHandler]) -> None:
        self._redis_url = redis_url
        self._queue_name = queue_name
        self._handlers = handlers
        self._worker: Worker | None = None

    @property
    def queue_name(self) -> QueueName:
        return self._queue_name

    def start(self) -> None:
        self._worker = Worker(self._queue_name.value, self._process_job, {"connection": self._redis_url})
        self._worker.on("failed", self._log_failed_job)
        log.info(
            "job_worker.started",
            extra={"queue": self._queue_name.value, "job_names": sorted(name.value for name in self._handlers)},
        )

    async def close(self) -> None:
        if self._worker is not None:
            await self._worker.close()
            self._worker = None

    async def _process_job(self, job: Job, _token: str) -> None:
        handler = self._handlers.get(job.name)
        if handler is None:
            raise UnrecoverableError(f"No handler for job {job.name} on queue {self._queue_name.value}")
        await handler.handle(job.data)

    def _log_failed_job(self, job: Job, error: Exception) -> None:
        log.warning(
            "job.failed",
            extra={
                "queue": self._queue_name.value,
                "job_name": job.name,
                "job_id": job.id,
                "attempts_made": job.attemptsMade,
                "error": str(error),
            },
        )

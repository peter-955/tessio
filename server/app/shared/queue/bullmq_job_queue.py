from collections.abc import Sequence

from bullmq import Queue
from pydantic import JsonValue

from app.shared.queue.job_queue import JobQueue
from app.shared.queue.job_schedule import JobSchedule
from app.shared.typing.constants import FAILED_JOB_RETENTION, JOB_ATTEMPTS, JOB_BACKOFF_DELAY
from app.shared.typing.enums import JobName, QueueName


class BullmqJobQueue(JobQueue):
    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._queues: dict[QueueName, Queue] = {}

    async def add(
        self, queue_name: QueueName, job_name: JobName, data: dict[str, JsonValue], job_id: str | None = None
    ) -> None:
        options = self._job_options()
        if job_id is not None:
            options["deduplication"] = {"id": job_id}
        await self._get_queue(queue_name).add(job_name.value, data, options)

    async def replace_schedules(self, schedules: Sequence[JobSchedule]) -> None:
        for queue_name in QueueName:
            queue_schedules = [schedule for schedule in schedules if schedule.queue_name is queue_name]
            wanted_scheduler_ids = {schedule.scheduler_id for schedule in queue_schedules}
            queue = self._get_queue(queue_name)
            for scheduler in await queue.getJobSchedulers():
                scheduler_id: str = scheduler["key"]
                if scheduler_id not in wanted_scheduler_ids:
                    await queue.removeJobScheduler(scheduler_id)
            for schedule in queue_schedules:
                await queue.upsertJobScheduler(
                    schedule.scheduler_id,
                    {"pattern": schedule.cron_pattern, "tz": schedule.timezone},
                    schedule.job_name.value,
                    {},
                    self._job_options(),
                )

    async def close(self) -> None:
        for queue in self._queues.values():
            await queue.close()
        self._queues.clear()

    def _get_queue(self, queue_name: QueueName) -> Queue:
        if queue_name not in self._queues:
            self._queues[queue_name] = Queue(queue_name.value, {"connection": self._redis_url})
        return self._queues[queue_name]

    @staticmethod
    def _job_options() -> dict[str, JsonValue]:
        return {
            "attempts": JOB_ATTEMPTS,
            "backoff": {"type": "exponential", "delay": int(JOB_BACKOFF_DELAY.total_seconds() * 1000)},
            "removeOnComplete": True,
            "removeOnFail": {"age": int(FAILED_JOB_RETENTION.total_seconds())},
        }

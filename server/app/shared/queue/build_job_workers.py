from collections.abc import Mapping

from app.shared.queue.bullmq_job_worker import BullmqJobWorker
from app.shared.queue.job_handler import JobHandler
from app.shared.typing.enums import JobName, QueueName


def build_job_workers(
    redis_url: str, handlers: Mapping[QueueName, Mapping[JobName, JobHandler]]
) -> list[BullmqJobWorker]:
    return [BullmqJobWorker(redis_url, queue_name, handlers.get(queue_name, {})) for queue_name in QueueName]

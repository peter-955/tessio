from collections.abc import Sequence

from redis.exceptions import RedisError

from app.modules.integrations.domains.chat_delivery_job.entity import ChatDeliveryJob
from app.modules.integrations.ports.chat_delivery_requester import ChatDeliveryRequester
from app.shared.logging import get_logger
from app.shared.queue import JobQueue
from app.shared.typing.enums import JobName, QueueName

log = get_logger(__name__)


class QueuedChatDeliveryRequester(ChatDeliveryRequester):
    def __init__(self, job_queue: JobQueue) -> None:
        self._job_queue = job_queue

    async def request(self, jobs: Sequence[ChatDeliveryJob]) -> None:
        for job in jobs:
            try:
                await self._job_queue.add(QueueName.INTEGRATIONS, JobName.CHAT_DELIVER, job.model_dump(mode="json"))
            except RedisError as error:
                log.warning(
                    "integrations.chat_enqueue_failed",
                    extra={
                        "chat_channel_id": str(job.chat_channel_id),
                        "event": job.event.value,
                        "reason": type(error).__name__,
                    },
                )

from uuid import UUID

from redis.exceptions import RedisError

from app.modules.integrations.ports.webhook_delivery_requester import WebhookDeliveryRequester
from app.modules.integrations.typing.constants.webhook import (
    WEBHOOK_DELIVERY_JOB_ID_KEY,
    WEBHOOK_DELIVERY_JOB_ID_PREFIX,
)
from app.shared.logging import get_logger
from app.shared.queue import JobQueue
from app.shared.typing.enums import JobName, QueueName

log = get_logger(__name__)


class QueuedWebhookDeliveryRequester(WebhookDeliveryRequester):
    def __init__(self, job_queue: JobQueue) -> None:
        self._job_queue = job_queue

    async def request(self, delivery_id: UUID) -> None:
        try:
            await self._job_queue.add(
                QueueName.INTEGRATIONS,
                JobName.WEBHOOK_DELIVER,
                {WEBHOOK_DELIVERY_JOB_ID_KEY: str(delivery_id)},
                job_id=f"{WEBHOOK_DELIVERY_JOB_ID_PREFIX}{delivery_id}",
            )
        except RedisError as error:
            log.warning(
                "integrations.webhook_enqueue_failed",
                extra={"delivery_id": str(delivery_id), "reason": type(error).__name__},
            )

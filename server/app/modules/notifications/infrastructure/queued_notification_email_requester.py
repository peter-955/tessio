from collections.abc import Sequence

from redis.exceptions import RedisError

from app.modules.notifications.domains.notification_email_job.entity import NotificationEmailJob
from app.modules.notifications.ports.notification_email_requester import NotificationEmailRequester
from app.shared.logging import get_logger
from app.shared.queue import JobQueue
from app.shared.typing.enums import JobName, QueueName

log = get_logger(__name__)


class QueuedNotificationEmailRequester(NotificationEmailRequester):
    def __init__(self, job_queue: JobQueue) -> None:
        self._job_queue = job_queue

    async def request(self, jobs: Sequence[NotificationEmailJob]) -> None:
        for job in jobs:
            try:
                await self._job_queue.add(QueueName.EMAIL, JobName.NOTIFICATION_EMAIL, job.model_dump(mode="json"))
            except RedisError as error:
                log.warning(
                    "notifications.email_enqueue_failed",
                    extra={
                        "user_id": str(job.user_id),
                        "kind": job.payload.kind.value,
                        "reason": type(error).__name__,
                    },
                )

from pydantic import JsonValue, ValidationError

from app.modules.notifications.domains.notification_email_job.entity import NotificationEmailJob
from app.modules.notifications.usecases.send_notification_email import SendNotificationEmailUseCase
from app.shared.logging import get_logger
from app.shared.queue import JobHandler

log = get_logger(__name__)


class SendNotificationEmailJobHandler(JobHandler):
    def __init__(self, use_case: SendNotificationEmailUseCase) -> None:
        self._use_case = use_case

    async def handle(self, data: dict[str, JsonValue]) -> None:
        try:
            job = NotificationEmailJob.model_validate(data)
        except ValidationError:
            log.warning("notifications.email_invalid_job_data")
            return
        await self._use_case.execute(job)

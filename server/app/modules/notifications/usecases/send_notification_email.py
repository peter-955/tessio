from app.modules.notifications.domains.notification_email_job.entity import NotificationEmailJob
from app.modules.notifications.domains.notification_preference.repository import NotificationPreferenceRepository
from app.modules.notifications.ports.notification_email_recipient_reader import NotificationEmailRecipientReader
from app.modules.notifications.typing.enums import NotificationChannel
from app.modules.notifications.utils.notification_email import build_notification_email
from app.modules.notifications.utils.notification_settings import is_channel_enabled
from app.shared.common import Transaction
from app.shared.logging import get_logger
from app.shared.mailer import Mailer

log = get_logger(__name__)


class SendNotificationEmailUseCase:
    def __init__(
        self,
        transaction: Transaction,
        notification_email_recipient_reader: NotificationEmailRecipientReader,
        notification_preference_repository: NotificationPreferenceRepository,
        mailer: Mailer,
        client_url: str,
    ) -> None:
        self._transaction = transaction
        self._notification_email_recipient_reader = notification_email_recipient_reader
        self._notification_preference_repository = notification_preference_repository
        self._mailer = mailer
        self._client_url = client_url

    async def execute(self, job: NotificationEmailJob) -> bool:
        kind = job.payload.kind
        async with self._transaction.begin():
            recipient = await self._notification_email_recipient_reader.find_active_recipient(
                job.user_id, job.project_id
            )
            preferences = await self._notification_preference_repository.list_for_users({job.user_id}, kind)
        if recipient is None or not is_channel_enabled(preferences, kind, NotificationChannel.EMAIL):
            log.info("notifications.email_skipped", extra={"user_id": str(job.user_id), "kind": kind.value})
            return False
        await self._mailer.send(build_notification_email(recipient, job.payload, self._client_url))
        return True

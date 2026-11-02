from collections.abc import Collection
from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.notifications.domains.notification.entity import Notification
from app.modules.notifications.domains.notification.repository import NotificationRepository
from app.modules.notifications.domains.notification_email_job.entity import NotificationEmailJob
from app.modules.notifications.domains.notification_payload.entity import NotificationPayload
from app.modules.notifications.domains.notification_preference.repository import NotificationPreferenceRepository
from app.modules.notifications.ports.notification_email_requester import NotificationEmailRequester
from app.modules.notifications.ports.recipient_directory import RecipientDirectory
from app.modules.notifications.typing.constants import ACTOR_EXCLUDED_KINDS
from app.modules.notifications.typing.enums import NotificationChannel
from app.modules.notifications.utils.notification_settings import group_by_user, is_channel_enabled
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType
from app.shared.permissions import ProjectRole


class SendNotificationUseCase:
    def __init__(
        self,
        transaction: Transaction,
        notification_repository: NotificationRepository,
        recipient_directory: RecipientDirectory,
        live_event_publisher: LiveEventPublisher,
        notification_preference_repository: NotificationPreferenceRepository,
        notification_email_requester: NotificationEmailRequester,
    ) -> None:
        self._transaction = transaction
        self._notification_repository = notification_repository
        self._recipient_directory = recipient_directory
        self._live_event_publisher = live_event_publisher
        self._notification_preference_repository = notification_preference_repository
        self._notification_email_requester = notification_email_requester

    async def execute(
        self,
        project_id: UUID,
        payload: NotificationPayload,
        actor_id: UUID | None,
        recipient_ids: Collection[UUID] = (),
        recipient_roles: Collection[ProjectRole] = (),
    ) -> list[Notification]:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            active_recipient_ids = await self._recipient_directory.list_active_recipient_ids(
                project_id, frozenset(recipient_ids), frozenset(recipient_roles)
            )
            if payload.kind in ACTOR_EXCLUDED_KINDS and actor_id is not None:
                active_recipient_ids = active_recipient_ids - {actor_id}
            preferences_by_user = group_by_user(
                await self._notification_preference_repository.list_for_users(active_recipient_ids, payload.kind)
            )
            ordered_recipient_ids = sorted(active_recipient_ids)
            notifications = [
                Notification(
                    id=uuid7(),
                    user_id=recipient_id,
                    project_id=project_id,
                    actor_id=actor_id,
                    kind=payload.kind,
                    payload=payload,
                    read_at=None,
                    created_at=now,
                )
                for recipient_id in ordered_recipient_ids
                if is_channel_enabled(preferences_by_user[recipient_id], payload.kind, NotificationChannel.IN_APP)
            ]
            if notifications:
                await self._notification_repository.add_all(notifications)
        for notification in notifications:
            await self._live_event_publisher.publish(
                LiveEvent(
                    type=LiveEventType.NOTIFICATION_CREATED,
                    user_id=notification.user_id,
                    project_id=notification.project_id,
                    ids={"notificationId": str(notification.id)},
                )
            )
        await self._notification_email_requester.request(
            [
                NotificationEmailJob(user_id=recipient_id, project_id=project_id, actor_id=actor_id, payload=payload)
                for recipient_id in ordered_recipient_ids
                if is_channel_enabled(preferences_by_user[recipient_id], payload.kind, NotificationChannel.EMAIL)
            ]
        )
        return notifications

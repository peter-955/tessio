from collections.abc import Collection
from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.notifications.domains.notification.entity import Notification
from app.modules.notifications.domains.notification.repository import NotificationRepository
from app.modules.notifications.domains.notification_payload.entity import NotificationPayload
from app.modules.notifications.ports.recipient_directory import RecipientDirectory
from app.modules.notifications.typing.constants import ACTOR_EXCLUDED_KINDS
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
    ) -> None:
        self._transaction = transaction
        self._notification_repository = notification_repository
        self._recipient_directory = recipient_directory
        self._live_event_publisher = live_event_publisher

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
                for recipient_id in sorted(active_recipient_ids)
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
        return notifications

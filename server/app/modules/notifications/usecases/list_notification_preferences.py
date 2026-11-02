from app.modules.notifications.domains.notification_preference.repository import NotificationPreferenceRepository
from app.modules.notifications.domains.notification_setting.entity import NotificationSetting
from app.modules.notifications.utils.notification_settings import build_notification_settings
from app.shared.common import Transaction
from app.shared.permissions import Actor


class ListNotificationPreferencesUseCase:
    def __init__(
        self, transaction: Transaction, notification_preference_repository: NotificationPreferenceRepository
    ) -> None:
        self._transaction = transaction
        self._notification_preference_repository = notification_preference_repository

    async def execute(self, actor: Actor) -> list[NotificationSetting]:
        async with self._transaction.begin():
            preferences = await self._notification_preference_repository.list_for_user(actor.user_id)
        return build_notification_settings(preferences)

from collections.abc import Sequence

from app.modules.notifications.domains.notification_preference.entity import NotificationPreference
from app.modules.notifications.domains.notification_preference.repository import NotificationPreferenceRepository
from app.modules.notifications.domains.notification_setting.entity import NotificationSetting
from app.modules.notifications.domains.notification_setting_change.entity import NotificationSettingChange
from app.modules.notifications.errors import NotificationKindRepeatedError
from app.modules.notifications.typing.enums import NotificationChannel
from app.modules.notifications.utils.notification_settings import build_notification_settings
from app.shared.common import Transaction
from app.shared.permissions import Actor


class UpdateNotificationPreferencesUseCase:
    def __init__(
        self, transaction: Transaction, notification_preference_repository: NotificationPreferenceRepository
    ) -> None:
        self._transaction = transaction
        self._notification_preference_repository = notification_preference_repository

    async def execute(self, actor: Actor, changes: Sequence[NotificationSettingChange]) -> list[NotificationSetting]:
        if len({change.kind for change in changes}) != len(changes):
            raise NotificationKindRepeatedError
        preferences = [
            NotificationPreference(user_id=actor.user_id, kind=change.kind, channel=channel, is_enabled=is_enabled)
            for change in changes
            for channel, is_enabled in (
                (NotificationChannel.IN_APP, change.is_in_app_enabled),
                (NotificationChannel.EMAIL, change.is_email_enabled),
            )
            if is_enabled is not None
        ]
        async with self._transaction.begin():
            await self._notification_preference_repository.save_all(preferences)
            stored_preferences = await self._notification_preference_repository.list_for_user(actor.user_id)
        return build_notification_settings(stored_preferences)

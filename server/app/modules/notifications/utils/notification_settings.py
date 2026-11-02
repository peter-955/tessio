from collections import defaultdict
from collections.abc import Iterable
from uuid import UUID

from app.modules.notifications.domains.notification_preference.entity import NotificationPreference
from app.modules.notifications.domains.notification_setting.entity import NotificationSetting
from app.modules.notifications.typing.constants import EMAIL_ON_BY_DEFAULT_KINDS
from app.modules.notifications.typing.enums import NotificationChannel, NotificationKind


def is_enabled_by_default(kind: NotificationKind, channel: NotificationChannel) -> bool:
    if channel is NotificationChannel.EMAIL:
        return kind in EMAIL_ON_BY_DEFAULT_KINDS
    return True


def is_channel_enabled(
    preferences: Iterable[NotificationPreference], kind: NotificationKind, channel: NotificationChannel
) -> bool:
    for preference in preferences:
        if preference.kind is kind and preference.channel is channel:
            return preference.is_enabled
    return is_enabled_by_default(kind, channel)


def build_notification_settings(preferences: Iterable[NotificationPreference]) -> list[NotificationSetting]:
    stored_preferences = list(preferences)
    return [
        NotificationSetting(
            kind=kind,
            is_in_app_enabled=is_channel_enabled(stored_preferences, kind, NotificationChannel.IN_APP),
            is_email_enabled=is_channel_enabled(stored_preferences, kind, NotificationChannel.EMAIL),
        )
        for kind in NotificationKind
    ]


def group_by_user(preferences: Iterable[NotificationPreference]) -> defaultdict[UUID, list[NotificationPreference]]:
    preferences_by_user: defaultdict[UUID, list[NotificationPreference]] = defaultdict(list)
    for preference in preferences:
        preferences_by_user[preference.user_id].append(preference)
    return preferences_by_user

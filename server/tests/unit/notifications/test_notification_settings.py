from uuid import uuid4

from app.modules.notifications import NotificationChannel, NotificationKind
from app.modules.notifications.domains.notification_preference.entity import NotificationPreference
from app.modules.notifications.utils.notification_settings import build_notification_settings, is_channel_enabled


def test_defaults_turn_in_app_on_and_email_on_only_for_assignments() -> None:
    settings = {setting.kind: setting for setting in build_notification_settings([])}

    assert list(settings) == list(NotificationKind)
    assert all(setting.is_in_app_enabled for setting in settings.values())
    assert {kind for kind, setting in settings.items() if setting.is_email_enabled} == {
        NotificationKind.GAP_ASSIGNED,
        NotificationKind.FAILURE_ASSIGNED,
    }


def test_a_stored_preference_overrides_the_default() -> None:
    user_id = uuid4()
    preferences = [
        NotificationPreference(
            user_id=user_id, kind=NotificationKind.GAP_ASSIGNED, channel=NotificationChannel.EMAIL, is_enabled=False
        ),
        NotificationPreference(
            user_id=user_id, kind=NotificationKind.RUN_FINISHED, channel=NotificationChannel.EMAIL, is_enabled=True
        ),
        NotificationPreference(
            user_id=user_id, kind=NotificationKind.RUN_FINISHED, channel=NotificationChannel.IN_APP, is_enabled=False
        ),
    ]

    assert not is_channel_enabled(preferences, NotificationKind.GAP_ASSIGNED, NotificationChannel.EMAIL)
    assert is_channel_enabled(preferences, NotificationKind.GAP_ASSIGNED, NotificationChannel.IN_APP)
    assert is_channel_enabled(preferences, NotificationKind.RUN_FINISHED, NotificationChannel.EMAIL)
    assert not is_channel_enabled(preferences, NotificationKind.RUN_FINISHED, NotificationChannel.IN_APP)
    assert is_channel_enabled(preferences, NotificationKind.FAILURE_ASSIGNED, NotificationChannel.EMAIL)

from app.modules.notifications.domains.notification_setting.entity import NotificationSetting
from app.modules.notifications.domains.notification_setting_change.entity import NotificationSettingChange
from app.modules.notifications.models.notification_preference_change_request import (
    NotificationPreferenceChangeRequest,
)
from app.modules.notifications.models.notification_preference_response import NotificationPreferenceResponse


def build_notification_preference_response(setting: NotificationSetting) -> NotificationPreferenceResponse:
    return NotificationPreferenceResponse(
        kind=setting.kind, in_app=setting.is_in_app_enabled, email=setting.is_email_enabled
    )


def build_notification_setting_change(request: NotificationPreferenceChangeRequest) -> NotificationSettingChange:
    return NotificationSettingChange(
        kind=request.kind, is_in_app_enabled=request.in_app, is_email_enabled=request.email
    )

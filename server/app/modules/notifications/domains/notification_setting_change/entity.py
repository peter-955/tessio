from app.modules.notifications.typing.enums import NotificationKind
from app.shared.common import Entity


class NotificationSettingChange(Entity):
    kind: NotificationKind
    is_in_app_enabled: bool | None
    is_email_enabled: bool | None

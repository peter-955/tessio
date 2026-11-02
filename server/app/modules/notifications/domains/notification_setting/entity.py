from app.modules.notifications.typing.enums import NotificationKind
from app.shared.common import Entity


class NotificationSetting(Entity):
    kind: NotificationKind
    is_in_app_enabled: bool
    is_email_enabled: bool

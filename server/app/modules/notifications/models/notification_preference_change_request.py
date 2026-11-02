from app.modules.notifications.typing.enums import NotificationKind
from app.shared.common import WireModel


class NotificationPreferenceChangeRequest(WireModel):
    kind: NotificationKind
    in_app: bool | None = None
    email: bool | None = None

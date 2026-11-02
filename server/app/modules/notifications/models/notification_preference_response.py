from app.modules.notifications.typing.enums import NotificationKind
from app.shared.common import WireModel


class NotificationPreferenceResponse(WireModel):
    kind: NotificationKind
    in_app: bool
    email: bool

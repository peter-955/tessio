from app.modules.notifications.typing.enums.notification import NotificationKind

MAX_PAYLOAD_TEXT_LENGTH = 200
TRUNCATION_MARK = "…"
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100
ACTOR_EXCLUDED_KINDS = frozenset({NotificationKind.GAP_ASSIGNED, NotificationKind.FAILURE_ASSIGNED})

from typing import Literal
from uuid import UUID

from app.modules.notifications.typing.enums import NotificationKind
from app.shared.common import WireModel


class GapAssignedPayloadResponse(WireModel):
    kind: Literal[NotificationKind.GAP_ASSIGNED]
    gap_id: UUID
    story_id: UUID
    story_jira_key: str
    question: str

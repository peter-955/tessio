from datetime import datetime
from uuid import UUID

from app.modules.gaps.typing.enums import GapSeverity, GapType
from app.shared.common import Entity


class GapToAnswerItem(Entity):
    gap_id: UUID
    story_jira_key: str
    question: str
    type: GapType
    severity: GapSeverity
    created_at: datetime

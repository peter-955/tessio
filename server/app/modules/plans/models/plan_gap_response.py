from datetime import datetime
from uuid import UUID

from app.modules.gaps.typing.enums import GapSeverity
from app.shared.common import WireModel
from app.shared.permissions import ProjectRole


class PlanGapResponse(WireModel):
    gap_id: UUID
    story_id: UUID
    story_jira_key: str
    question: str
    severity: GapSeverity
    assignee_id: UUID | None
    assignee_name: str | None
    assignee_role: ProjectRole | None
    created_at: datetime

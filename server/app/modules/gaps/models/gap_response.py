from datetime import datetime
from uuid import UUID

from app.modules.gaps.typing.enums import GapDataScope, GapSeverity, GapStatus, GapTargetType, GapType
from app.modules.users import UserStatus
from app.shared.common import WireModel
from app.shared.permissions import ProjectRole


class GapResponse(WireModel):
    id: UUID
    project_key: str
    project_name: str
    story_id: UUID
    story_jira_key: str
    story_title: str
    target_type: GapTargetType
    target_id: UUID | None
    target_ref: str | None
    type: GapType
    data_scope: GapDataScope | None
    severity: GapSeverity
    question: str
    status: GapStatus
    assignee_id: UUID | None
    assignee_name: str | None
    assignee_status: UserStatus | None
    assignee_role: ProjectRole | None
    raised_by: UUID
    raised_by_name: str
    is_raised_via_claude: bool
    answer: str | None
    answered_by: UUID | None
    answered_by_name: str | None
    answered_at: datetime | None
    reopened_by_name: str | None
    reopened_at: datetime | None
    created_at: datetime

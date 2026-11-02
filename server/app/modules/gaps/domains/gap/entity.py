from datetime import datetime
from uuid import UUID

from app.modules.gaps.typing.enums import GapDataScope, GapSeverity, GapStatus, GapTargetType, GapType
from app.shared.common import Entity
from app.shared.permissions import ProjectRole


class Gap(Entity):
    id: UUID
    project_id: UUID
    story_id: UUID
    target_type: GapTargetType
    target_id: UUID | None
    type: GapType
    data_scope: GapDataScope | None
    severity: GapSeverity
    question: str
    status: GapStatus
    assignee_id: UUID | None
    assignee_role: ProjectRole | None
    raised_by: UUID
    raised_via_token_id: UUID | None
    answer: str | None
    answered_by: UUID | None
    answered_at: datetime | None
    answered_via_token_id: UUID | None
    reopened_by: UUID | None
    reopened_at: datetime | None
    created_at: datetime

    @property
    def is_open(self) -> bool:
        return self.status is GapStatus.OPEN

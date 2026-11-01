from uuid import UUID

from app.modules.gaps.typing.enums import GapDataScope, GapSeverity, GapTargetType, GapType
from app.shared.common import Entity


class GapDraft(Entity):
    type: GapType
    severity: GapSeverity
    target_type: GapTargetType
    target_ref: str | None
    question: str
    data_scope: GapDataScope | None
    assignee_id: UUID | None

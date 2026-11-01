from datetime import datetime
from uuid import UUID

from app.modules.runs import CriterionStatus
from app.shared.common import WireModel


class CriterionTraceResponse(WireModel):
    id: UUID
    code: str
    position: int
    text: str
    removed_at: datetime | None
    status: CriterionStatus
    linked_case_ids: list[UUID]

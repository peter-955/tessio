from datetime import datetime
from uuid import UUID

from app.shared.common import WireModel


class AcceptanceCriterionResponse(WireModel):
    id: UUID
    code: str
    position: int
    text: str
    removed_at: datetime | None
    is_removed: bool

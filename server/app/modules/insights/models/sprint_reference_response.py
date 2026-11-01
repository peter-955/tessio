from datetime import datetime
from uuid import UUID

from app.modules.stories import SprintState
from app.shared.common import WireModel


class SprintReferenceResponse(WireModel):
    id: UUID
    name: str
    state: SprintState
    start_at: datetime | None
    end_at: datetime | None

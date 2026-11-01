from datetime import datetime
from uuid import UUID

from app.modules.runs import RunStatus
from app.shared.common import WireModel


class RunReferenceResponse(WireModel):
    id: UUID
    status: RunStatus
    started_at: datetime
    finished_at: datetime | None

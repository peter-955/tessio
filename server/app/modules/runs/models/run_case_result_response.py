from datetime import datetime
from uuid import UUID

from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import WireModel


class RunCaseResultResponse(WireModel):
    id: UUID
    status: ResultStatus
    duration_ms: int | None
    recorded_at: datetime

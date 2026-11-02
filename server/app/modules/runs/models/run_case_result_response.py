from datetime import datetime
from uuid import UUID

from app.modules.runs.typing.enums import ResultStatus, SuspectedCause
from app.shared.common import WireModel


class RunCaseResultResponse(WireModel):
    id: UUID
    status: ResultStatus
    duration_ms: int | None
    suspected_cause: SuspectedCause | None
    cause_reason: str | None
    recorded_at: datetime
    iteration: int

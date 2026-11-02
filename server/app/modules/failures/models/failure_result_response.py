from datetime import datetime
from uuid import UUID

from app.modules.runs import ResultStatus, RunExecutor, RunStatus
from app.shared.common import WireModel


class FailureResultResponse(WireModel):
    case_result_id: UUID
    run_id: UUID
    run_status: RunStatus
    run_executor: RunExecutor
    status: ResultStatus
    duration_ms: int | None
    recorded_at: datetime
    started_by_name: str
    iteration: int | None

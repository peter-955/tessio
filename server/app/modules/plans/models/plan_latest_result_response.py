from datetime import datetime
from uuid import UUID

from app.modules.runs import ResultStatus
from app.shared.common import WireModel


class PlanLatestResultResponse(WireModel):
    case_result_id: UUID
    run_id: UUID
    status: ResultStatus
    recorded_at: datetime

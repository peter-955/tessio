from uuid import UUID

from app.modules.runs.models.manual_step_result_response import ManualStepResultResponse
from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import WireModel


class ManualCaseResultResponse(WireModel):
    id: UUID
    run_id: UUID
    test_case_id: UUID
    status: ResultStatus
    suggested_status: ResultStatus
    duration_ms: int | None
    steps: list[ManualStepResultResponse]

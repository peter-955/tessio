from uuid import UUID

from app.modules.runs.models.run_case_result_response import RunCaseResultResponse
from app.modules.runs.models.step_result_response import StepResultResponse
from app.shared.common import WireModel


class RunCaseResponse(WireModel):
    test_case_id: UUID
    code: str
    title: str
    version_id: UUID
    version_number: int
    position: int
    result: RunCaseResultResponse | None
    steps: list[StepResultResponse]

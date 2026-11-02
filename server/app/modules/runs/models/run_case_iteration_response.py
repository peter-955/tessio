from app.modules.runs.models.run_case_result_response import RunCaseResultResponse
from app.modules.runs.models.step_result_response import StepResultResponse
from app.shared.common import WireModel


class RunCaseIterationResponse(WireModel):
    iteration: int
    values: dict[str, str]
    result: RunCaseResultResponse | None
    steps: list[StepResultResponse]

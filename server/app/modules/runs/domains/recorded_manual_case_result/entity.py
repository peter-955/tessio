from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.step_result.entity import StepResult
from app.modules.runs.typing.enums import ResultStatus
from app.shared.common import Entity


class RecordedManualCaseResult(Entity):
    case_result: CaseResult
    step_results: list[StepResult]
    suggested_status: ResultStatus

from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.step_result_view.entity import StepResultView
from app.shared.common import Entity


class RunCaseIteration(Entity):
    iteration: int
    values: dict[str, str]
    result: CaseResult | None
    steps: list[StepResultView]

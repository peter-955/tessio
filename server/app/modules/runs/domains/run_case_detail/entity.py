from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.runs.domains.step_result_view.entity import StepResultView
from app.shared.common import Entity


class RunCaseDetail(Entity):
    view: RunCaseView
    result: CaseResult | None
    steps: list[StepResultView]

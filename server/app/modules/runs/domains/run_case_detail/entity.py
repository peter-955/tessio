from pydantic import Field

from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.run_case_file.entity import RunCaseFile
from app.modules.runs.domains.run_case_iteration.entity import RunCaseIteration
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.runs.domains.run_criterion.entity import RunCriterion
from app.modules.runs.domains.step_result_view.entity import StepResultView
from app.shared.common import Entity


class RunCaseDetail(Entity):
    view: RunCaseView
    result: CaseResult | None
    steps: list[StepResultView]
    criteria: list[RunCriterion]
    files: list[RunCaseFile]
    iterations: list[RunCaseIteration] = Field(default_factory=list)

from uuid import UUID

from app.modules.runs.models.run_case_file_response import RunCaseFileResponse
from app.modules.runs.models.run_case_iteration_response import RunCaseIterationResponse
from app.modules.runs.models.run_case_result_response import RunCaseResultResponse
from app.modules.runs.models.run_criterion_response import RunCriterionResponse
from app.modules.runs.models.step_result_response import StepResultResponse
from app.shared.common import WireModel


class RunCaseResponse(WireModel):
    test_case_id: UUID
    code: str
    title: str
    version_id: UUID
    version_number: int
    position: int
    business_value: str | None
    preconditions: str | None
    criteria: list[RunCriterionResponse]
    files: list[RunCaseFileResponse]
    result: RunCaseResultResponse | None
    steps: list[StepResultResponse]
    parameters: list[str]
    iterations: list[RunCaseIterationResponse]
    story_id: UUID | None = None
    story_jira_key: str | None = None
    story_title: str | None = None

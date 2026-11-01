from app.modules.insights.models.draft_case_list_response import DraftCaseListResponse
from app.modules.insights.models.failure_to_fix_list_response import FailureToFixListResponse
from app.modules.insights.models.gap_to_answer_list_response import GapToAnswerListResponse
from app.modules.insights.models.sprint_reference_response import SprintReferenceResponse
from app.modules.insights.models.uncovered_criterion_list_response import UncoveredCriterionListResponse
from app.modules.insights.typing.enums import MyWorkSection
from app.shared.common import WireModel
from app.shared.permissions import ProjectRole


class MyWorkResponse(WireModel):
    role: ProjectRole
    sections: list[MyWorkSection]
    sprint: SprintReferenceResponse | None
    uncovered_criteria: UncoveredCriterionListResponse
    draft_cases: DraftCaseListResponse
    failures_to_fix: FailureToFixListResponse
    gaps_to_answer: GapToAnswerListResponse
    unassigned_failure_count: int

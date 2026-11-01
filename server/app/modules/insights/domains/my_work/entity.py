from app.modules.insights.domains.draft_case_list.entity import DraftCaseList
from app.modules.insights.domains.failure_to_fix_list.entity import FailureToFixList
from app.modules.insights.domains.gap_to_answer_list.entity import GapToAnswerList
from app.modules.insights.domains.sprint_reference.entity import SprintReference
from app.modules.insights.domains.uncovered_criterion_list.entity import UncoveredCriterionList
from app.modules.insights.typing.enums import MyWorkSection
from app.shared.common import Entity
from app.shared.permissions import ProjectRole


class MyWork(Entity):
    role: ProjectRole
    sections: list[MyWorkSection]
    sprint: SprintReference | None
    uncovered_criteria: UncoveredCriterionList
    draft_cases: DraftCaseList
    failures_to_fix: FailureToFixList
    gaps_to_answer: GapToAnswerList
    unassigned_failure_count: int

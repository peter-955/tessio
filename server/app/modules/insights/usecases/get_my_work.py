from uuid import UUID

from app.modules.insights.domains.draft_case_list.entity import DraftCaseList
from app.modules.insights.domains.failure_to_fix_list.entity import FailureToFixList
from app.modules.insights.domains.gap_to_answer_list.entity import GapToAnswerList
from app.modules.insights.domains.my_work.entity import MyWork
from app.modules.insights.domains.sprint_reference.entity import SprintReference
from app.modules.insights.domains.uncovered_criterion_list.entity import UncoveredCriterionList
from app.modules.insights.ports.activity_reader import ActivityReader
from app.modules.insights.ports.coverage_reader import CoverageReader
from app.modules.insights.ports.story_scope_reader import StoryScopeReader
from app.modules.insights.typing.constants import MAX_MY_WORK_ITEMS, SECTIONS_BY_ROLE
from app.modules.insights.typing.enums import MyWorkSection
from app.modules.insights.utils.coverage import build_criterion_traces
from app.modules.insights.utils.sprint_scope import resolve_sprint
from app.modules.insights.utils.uncovered_criteria import list_uncovered_criteria
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class GetMyWorkUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        story_scope_reader: StoryScopeReader,
        coverage_reader: CoverageReader,
        activity_reader: ActivityReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._story_scope_reader = story_scope_reader
        self._coverage_reader = coverage_reader
        self._activity_reader = activity_reader

    async def execute(self, actor: Actor, project_key: str, sprint_id: UUID | None) -> MyWork:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            if access.role is None:
                raise ProjectNotFoundError
            role = access.role
            project_id = access.project_id
            sections = SECTIONS_BY_ROLE[role]
            sprint = await resolve_sprint(self._story_scope_reader, project_id, sprint_id)
            uncovered_criteria = UncoveredCriterionList(total_count=0, items=[])
            draft_cases = DraftCaseList(total_count=0, items=[])
            failures_to_fix = FailureToFixList(total_count=0, items=[])
            gaps_to_answer = GapToAnswerList(total_count=0, items=[])
            if MyWorkSection.CASES_TO_WRITE in sections:
                uncovered_criteria = await self._list_uncovered_criteria(project_id, sprint)
                draft_cases = await self._activity_reader.list_draft_cases(project_id, actor.user_id, MAX_MY_WORK_ITEMS)
            if MyWorkSection.FAILURES_TO_FIX in sections:
                failures_to_fix = await self._activity_reader.list_failures_to_fix(
                    project_id, actor.user_id, MAX_MY_WORK_ITEMS
                )
            if MyWorkSection.GAPS_TO_ANSWER in sections:
                gaps_to_answer = await self._activity_reader.list_gaps_to_answer(
                    project_id, actor.user_id, role, MAX_MY_WORK_ITEMS
                )
            unassigned_failure_count = await self._activity_reader.count_unassigned_failures(project_id)
        return MyWork(
            role=role,
            sections=list(sections),
            sprint=sprint,
            uncovered_criteria=uncovered_criteria,
            draft_cases=draft_cases,
            failures_to_fix=failures_to_fix,
            gaps_to_answer=gaps_to_answer,
            unassigned_failure_count=unassigned_failure_count,
        )

    async def _list_uncovered_criteria(
        self, project_id: UUID, sprint: SprintReference | None
    ) -> UncoveredCriterionList:
        if sprint is None:
            return UncoveredCriterionList(total_count=0, items=[])
        stories = await self._story_scope_reader.list_stories(project_id, sprint.id, True)
        story_ids = [story.id for story in stories]
        criteria = await self._coverage_reader.list_criteria(project_id, story_ids)
        cases = await self._coverage_reader.list_cases(project_id, story_ids, False)
        return list_uncovered_criteria(stories, build_criterion_traces(criteria, cases), MAX_MY_WORK_ITEMS)

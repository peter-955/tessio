from app.modules.insights.domains.traceability.entity import Traceability
from app.modules.insights.ports.coverage_reader import CoverageReader
from app.modules.insights.ports.story_scope_reader import StoryScopeReader
from app.modules.insights.utils.coverage import build_criterion_traces, count_coverage
from app.modules.stories import StoryNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetTraceabilityUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        story_scope_reader: StoryScopeReader,
        coverage_reader: CoverageReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._story_scope_reader = story_scope_reader
        self._coverage_reader = coverage_reader

    async def execute(self, actor: Actor, project_key: str, jira_key: str) -> Traceability:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            story = await self._story_scope_reader.find_story(access.project_id, jira_key)
            if story is None:
                raise StoryNotFoundError
            criteria = await self._coverage_reader.list_criteria(access.project_id, [story.id])
            cases = await self._coverage_reader.list_cases(access.project_id, [story.id], False)
        traces = build_criterion_traces(criteria, cases)
        return Traceability(story=story, criteria=traces, cases=cases, coverage=count_coverage(traces))

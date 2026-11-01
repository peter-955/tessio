from uuid import UUID

from app.modules.insights.domains.dashboard_summary.entity import DashboardSummary
from app.modules.insights.ports.activity_reader import ActivityReader
from app.modules.insights.ports.coverage_reader import CoverageReader
from app.modules.insights.ports.story_scope_reader import StoryScopeReader
from app.modules.insights.utils.coverage import build_criterion_traces, count_coverage
from app.modules.insights.utils.sprint_scope import resolve_sprint
from app.modules.insights.utils.test_status_counts import count_test_statuses
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetDashboardUseCase:
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

    async def execute(self, actor: Actor, project_key: str, sprint_id: UUID | None) -> DashboardSummary:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            sprint = await resolve_sprint(self._story_scope_reader, access.project_id, sprint_id)
            stories = (
                []
                if sprint is None
                else await self._story_scope_reader.list_stories(access.project_id, sprint.id, True)
            )
            story_ids = [story.id for story in stories]
            criteria = await self._coverage_reader.list_criteria(access.project_id, story_ids)
            cases = await self._coverage_reader.list_cases(access.project_id, story_ids, False)
            open_gap_counts = await self._activity_reader.count_open_gaps(access.project_id, story_ids)
            active_failure_counts = await self._activity_reader.count_active_failures(access.project_id, story_ids)
        return DashboardSummary(
            sprint=sprint,
            story_count=len(stories),
            test_status_counts=count_test_statuses(stories),
            open_gap_count=sum(open_gap_counts.values()),
            active_failure_count=sum(active_failure_counts.values()),
            coverage=count_coverage(build_criterion_traces(criteria, cases)),
        )

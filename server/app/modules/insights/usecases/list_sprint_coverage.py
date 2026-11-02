from datetime import UTC, date, datetime

from app.modules.insights.domains.sprint_coverage.entity import SprintCoverage
from app.modules.insights.ports.coverage_reader import CoverageReader
from app.modules.insights.ports.story_scope_reader import StoryScopeReader
from app.modules.insights.typing.constants import MAX_SPRINT_COVERAGE_COUNT
from app.modules.insights.utils.coverage import build_criterion_traces, count_coverage
from app.modules.insights.utils.day_bounds import resolve_range_bounds
from app.modules.insights.utils.day_range import resolve_day_range
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListSprintCoverageUseCase:
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

    async def execute(
        self, actor: Actor, project_key: str, first_day: date | None, last_day: date | None
    ) -> list[SprintCoverage]:
        day_range = resolve_day_range(first_day, last_day, datetime.now(UTC).date())
        start_at, end_at = resolve_range_bounds(day_range)
        coverages: list[SprintCoverage] = []
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            sprints = await self._story_scope_reader.list_sprints_overlapping(
                access.project_id, start_at, end_at, MAX_SPRINT_COVERAGE_COUNT
            )
            for sprint in sprints:
                stories = await self._story_scope_reader.list_stories(access.project_id, sprint.id, True)
                story_ids = [story.id for story in stories]
                criteria = await self._coverage_reader.list_criteria(access.project_id, story_ids)
                cases = await self._coverage_reader.list_cases(access.project_id, story_ids, False)
                coverages.append(
                    SprintCoverage(
                        sprint=sprint,
                        story_count=len(stories),
                        coverage=count_coverage(build_criterion_traces(criteria, cases)),
                    )
                )
        return coverages

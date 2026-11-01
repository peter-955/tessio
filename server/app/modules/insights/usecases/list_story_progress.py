from uuid import UUID

from app.modules.insights.domains.story_progress.entity import StoryProgress
from app.modules.insights.ports.activity_reader import ActivityReader
from app.modules.insights.ports.coverage_reader import CoverageReader
from app.modules.insights.ports.story_scope_reader import StoryScopeReader
from app.modules.insights.utils.coverage import build_criterion_traces, count_coverage, count_coverage_by_story
from app.modules.insights.utils.sprint_scope import require_sprint
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListStoryProgressUseCase:
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

    async def execute(self, actor: Actor, project_key: str, sprint_id: UUID | None) -> list[StoryProgress]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            if sprint_id is not None:
                await require_sprint(self._story_scope_reader, access.project_id, sprint_id)
            stories = await self._story_scope_reader.list_stories(access.project_id, sprint_id, False)
            story_ids = [story.id for story in stories]
            criteria = await self._coverage_reader.list_criteria(access.project_id, story_ids)
            cases = await self._coverage_reader.list_cases(access.project_id, story_ids, False)
            open_gap_counts = await self._activity_reader.count_open_gaps(access.project_id, story_ids)
            active_failure_counts = await self._activity_reader.count_active_failures(access.project_id, story_ids)
            last_runs = await self._activity_reader.find_last_runs(access.project_id, story_ids)
        coverage_by_story = count_coverage_by_story(build_criterion_traces(criteria, cases))
        empty_coverage = count_coverage([])
        return [
            StoryProgress(
                story_id=story.id,
                jira_key=story.jira_key,
                coverage=coverage_by_story.get(story.id, empty_coverage),
                open_gap_count=open_gap_counts.get(story.id, 0),
                active_failure_count=active_failure_counts.get(story.id, 0),
                last_run=last_runs.get(story.id),
            )
            for story in stories
        ]

from uuid import UUID

from app.modules.runs.domains.run_filter.entity import RunFilter
from app.modules.runs.domains.run_summary.entity import RunSummary
from app.modules.runs.ports.run_target_reader import RunTargetReader
from app.modules.runs.ports.run_view_reader import RunViewReader
from app.modules.runs.typing.enums import RunStatus
from app.modules.stories import StoryNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListRunsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        run_target_reader: RunTargetReader,
        run_view_reader: RunViewReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._run_target_reader = run_target_reader
        self._run_view_reader = run_view_reader

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        story_key: str | None,
        status: RunStatus | None,
        limit: int,
        test_suite_id: UUID | None = None,
    ) -> list[RunSummary]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.RUN_VIEW)
            story_id: UUID | None = None
            if story_key is not None:
                story = await self._run_target_reader.find_story(access.project_id, story_key)
                if story is None:
                    raise StoryNotFoundError
                story_id = story.id
            summaries = await self._run_view_reader.list_summaries(
                access.project_id,
                RunFilter(story_id=story_id, status=status, limit=limit, test_suite_id=test_suite_id),
            )
        return summaries

from app.modules.stories.domains.story.repository import StoryRepository
from app.modules.stories.domains.story_filter.entity import StoryFilter
from app.modules.stories.domains.story_summary.entity import StorySummary
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListStoriesUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        story_repository: StoryRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._story_repository = story_repository

    async def execute(self, actor: Actor, project_key: str, story_filter: StoryFilter) -> list[StorySummary]:
        query = None if story_filter.query is None else story_filter.query.strip() or None
        normalized_filter = story_filter.model_copy(update={"query": query})
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.STORY_VIEW)
            return await self._story_repository.list_summaries(access.project_id, normalized_filter)

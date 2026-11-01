from app.modules.stories import StoryNotFoundError
from app.modules.story_context.domains.story_context.entity import StoryContext
from app.modules.story_context.ports.story_context_reader import StoryContextReader
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class GetStoryContextUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        story_context_reader: StoryContextReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._story_context_reader = story_context_reader

    async def execute_in_token_project(self, actor: Actor, story_key: str) -> StoryContext:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.STORY_VIEW)
            require(access, Capability.TEST_CASE_VIEW)
            require(access, Capability.TEST_DATA_VIEW)
            story = await self._story_context_reader.find_story(access.project_id, story_key)
            if story is None:
                raise StoryNotFoundError
            criteria = await self._story_context_reader.list_criteria(story.id)
            cases = await self._story_context_reader.list_ready_cases(story.id)
            other_case_count = await self._story_context_reader.count_other_cases(story.id)
            used_keys = {key for case in cases for key in case.data_keys}
            data_entries = [
                entry
                for entry in await self._story_context_reader.list_data_entries(access.project_id)
                if entry.key in used_keys
            ]
            environments = await self._story_context_reader.list_environments(access.project_id)
        return StoryContext(
            story=story,
            criteria=criteria,
            cases=cases,
            other_case_count=other_case_count,
            data_entries=data_entries,
            environments=environments,
        )

from app.modules.stories.domains.acceptance_criterion.repository import AcceptanceCriterionRepository
from app.modules.stories.domains.sprint.repository import SprintRepository
from app.modules.stories.domains.story.repository import StoryRepository
from app.modules.stories.domains.story_detail.entity import StoryDetail
from app.modules.stories.errors import StoryNotFoundError
from app.modules.stories.utils.story_detail import build_story_detail
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetStoryUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        story_repository: StoryRepository,
        sprint_repository: SprintRepository,
        acceptance_criterion_repository: AcceptanceCriterionRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._story_repository = story_repository
        self._sprint_repository = sprint_repository
        self._acceptance_criterion_repository = acceptance_criterion_repository

    async def execute(self, actor: Actor, project_key: str, jira_key: str) -> StoryDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.STORY_VIEW)
            story = await self._story_repository.find_by_jira_key(access.project_id, jira_key.upper())
            if story is None:
                raise StoryNotFoundError
            sprint = (
                None
                if story.sprint_id is None
                else await self._sprint_repository.find_by_id(access.project_id, story.sprint_id)
            )
            criteria = await self._acceptance_criterion_repository.list_for_story(story.id)
        return build_story_detail(access, story, sprint, criteria)

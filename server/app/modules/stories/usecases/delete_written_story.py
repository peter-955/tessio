from app.modules.stories.domains.acceptance_criterion.repository import AcceptanceCriterionRepository
from app.modules.stories.domains.story.repository import StoryRepository
from app.modules.stories.errors import StoriesComeFromJiraError, StoryInUseError, StoryNotFoundError
from app.modules.stories.ports.story_usage_checker import StoryUsageChecker
from app.modules.stories.utils.story_event import build_story_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class DeleteWrittenStoryUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        story_repository: StoryRepository,
        acceptance_criterion_repository: AcceptanceCriterionRepository,
        story_usage_checker: StoryUsageChecker,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._story_repository = story_repository
        self._acceptance_criterion_repository = acceptance_criterion_repository
        self._story_usage_checker = story_usage_checker
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, story_key: str) -> None:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.STORY_EDIT)
            story = await self._story_repository.find_by_jira_key_for_update(access.project_id, story_key.upper())
            if story is None:
                raise StoryNotFoundError
            if not story.is_written_in_tessio:
                raise StoriesComeFromJiraError
            if await self._story_usage_checker.is_in_use(story.id):
                raise StoryInUseError
            await self._acceptance_criterion_repository.delete_for_story(story.id)
            await self._story_repository.delete(story.id)
        await self._live_event_publisher.publish(build_story_changed_event(access.project_id, story))

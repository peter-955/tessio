from datetime import UTC, datetime

from app.modules.stories.domains.acceptance_criterion.repository import AcceptanceCriterionRepository
from app.modules.stories.domains.story.repository import StoryRepository
from app.modules.stories.domains.story_detail.entity import StoryDetail
from app.modules.stories.domains.written_story.entity import WrittenStory
from app.modules.stories.errors import StoriesComeFromJiraError, StoryNotFoundError
from app.modules.stories.ports.criteria_changed_handler import CriteriaChangedHandler
from app.modules.stories.utils.criteria_merge import merge_acceptance_criteria
from app.modules.stories.utils.plain_text_document import build_plain_text_document
from app.modules.stories.utils.story_detail import build_story_detail
from app.modules.stories.utils.story_event import build_story_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class UpdateWrittenStoryUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        story_repository: StoryRepository,
        acceptance_criterion_repository: AcceptanceCriterionRepository,
        criteria_changed_handler: CriteriaChangedHandler,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._story_repository = story_repository
        self._acceptance_criterion_repository = acceptance_criterion_repository
        self._criteria_changed_handler = criteria_changed_handler
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, story_key: str, written_story: WrittenStory) -> StoryDetail:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.STORY_EDIT)
            story = await self._story_repository.find_by_jira_key_for_update(access.project_id, story_key.upper())
            if story is None:
                raise StoryNotFoundError
            if not story.is_written_in_tessio:
                raise StoriesComeFromJiraError
            updated_story = story.model_copy(
                update={
                    "title": written_story.title,
                    "description": build_plain_text_document(written_story.description),
                    "jira_updated_at": now,
                }
            )
            await self._story_repository.save(updated_story)
            merge = merge_acceptance_criteria(
                access.project_id,
                story.id,
                await self._acceptance_criterion_repository.list_for_story(story.id),
                written_story.criteria,
                now,
            )
            for criterion in merge.criteria_to_save:
                await self._acceptance_criterion_repository.save(criterion)
            if merge.change.has_changed_or_removed:
                await self._criteria_changed_handler.handle(merge.change)
            criteria = await self._acceptance_criterion_repository.list_for_story(story.id)
        await self._live_event_publisher.publish(build_story_changed_event(access.project_id, updated_story))
        return build_story_detail(access, updated_story, None, criteria)

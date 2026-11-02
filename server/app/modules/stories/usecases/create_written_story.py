from datetime import UTC, datetime
from uuid import uuid7

from app.modules.stories.domains.acceptance_criterion.repository import AcceptanceCriterionRepository
from app.modules.stories.domains.story.entity import Story
from app.modules.stories.domains.story.repository import StoryRepository
from app.modules.stories.domains.story_detail.entity import StoryDetail
from app.modules.stories.domains.story_key_counter.repository import StoryKeyCounterRepository
from app.modules.stories.domains.written_story.entity import WrittenStory
from app.modules.stories.errors import StoriesComeFromJiraError
from app.modules.stories.ports.sync_target_reader import SyncTargetReader
from app.modules.stories.typing.constants import (
    WRITTEN_STORY_ISSUE_TYPE,
    WRITTEN_STORY_JIRA_ID_TEMPLATE,
    WRITTEN_STORY_KEY_TEMPLATE,
)
from app.modules.stories.typing.enums import StorySource, TestStatus
from app.modules.stories.utils.criteria_merge import merge_acceptance_criteria
from app.modules.stories.utils.plain_text_document import build_plain_text_document
from app.modules.stories.utils.story_detail import build_story_detail
from app.modules.stories.utils.story_event import build_story_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class CreateWrittenStoryUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        sync_target_reader: SyncTargetReader,
        story_repository: StoryRepository,
        acceptance_criterion_repository: AcceptanceCriterionRepository,
        story_key_counter_repository: StoryKeyCounterRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._sync_target_reader = sync_target_reader
        self._story_repository = story_repository
        self._acceptance_criterion_repository = acceptance_criterion_repository
        self._story_key_counter_repository = story_key_counter_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, written_story: WrittenStory) -> StoryDetail:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.STORY_EDIT)
            target = await self._sync_target_reader.find(access.project_id)
            if target is None:
                raise ProjectNotFoundError
            if target.jira_project_key is not None:
                raise StoriesComeFromJiraError
            number = await self._story_key_counter_repository.allocate_number(access.project_id, now)
            story_id = uuid7()
            story = Story(
                id=story_id,
                project_id=access.project_id,
                sprint_id=None,
                jira_id=WRITTEN_STORY_JIRA_ID_TEMPLATE.format(story_id=story_id),
                jira_key=WRITTEN_STORY_KEY_TEMPLATE.format(project_key=target.project_key, number=number),
                jira_url="",
                title=written_story.title,
                description=build_plain_text_document(written_story.description),
                jira_status="",
                jira_issue_type=WRITTEN_STORY_ISSUE_TYPE,
                test_status=TestStatus.NOT_STARTED,
                test_status_changed_at=None,
                test_status_changed_by=None,
                jira_updated_at=now,
                synced_at=now,
                jira_missing_at=None,
                created_at=now,
                source=StorySource.TESSIO,
            )
            await self._story_repository.save(story)
            merge = merge_acceptance_criteria(access.project_id, story.id, [], written_story.criteria, now)
            for criterion in merge.criteria_to_save:
                await self._acceptance_criterion_repository.save(criterion)
        await self._live_event_publisher.publish(build_story_changed_event(access.project_id, story))
        return build_story_detail(access, story, None, merge.criteria_to_save)

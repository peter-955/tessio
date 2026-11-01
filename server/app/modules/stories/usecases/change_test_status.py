from datetime import UTC, datetime

from app.modules.stories.domains.acceptance_criterion.repository import AcceptanceCriterionRepository
from app.modules.stories.domains.sprint.repository import SprintRepository
from app.modules.stories.domains.story.repository import StoryRepository
from app.modules.stories.domains.story_detail.entity import StoryDetail
from app.modules.stories.errors import InvalidTestStatusTransitionError, StoryNotFoundError, StorySignOffBlockedError
from app.modules.stories.ports.active_failure_counter import ActiveFailureCounter
from app.modules.stories.ports.running_run_checker import RunningRunChecker
from app.modules.stories.typing.constants import TEST_STATUS_TRANSITIONS
from app.modules.stories.typing.enums import TestStatus
from app.modules.stories.utils.story_detail import build_story_detail
from app.modules.stories.utils.test_status_transition import find_required_capability
from app.shared.common import Transaction
from app.shared.events import LiveEvent, LiveEventPublisher, LiveEventType
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ChangeTestStatusUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        story_repository: StoryRepository,
        sprint_repository: SprintRepository,
        acceptance_criterion_repository: AcceptanceCriterionRepository,
        active_failure_counter: ActiveFailureCounter,
        running_run_checker: RunningRunChecker,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._story_repository = story_repository
        self._sprint_repository = sprint_repository
        self._acceptance_criterion_repository = acceptance_criterion_repository
        self._active_failure_counter = active_failure_counter
        self._running_run_checker = running_run_checker
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, jira_key: str, test_status: TestStatus) -> StoryDetail:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.STORY_VIEW)
            required_capability = find_required_capability(test_status)
            if required_capability is not None:
                require(access, required_capability)
            story = await self._story_repository.find_by_jira_key_for_update(access.project_id, jira_key.upper())
            if story is None:
                raise StoryNotFoundError
            is_changing = test_status is not story.test_status
            if is_changing:
                if required_capability is None:
                    raise InvalidTestStatusTransitionError
                if test_status not in TEST_STATUS_TRANSITIONS[story.test_status]:
                    raise InvalidTestStatusTransitionError
                if test_status is TestStatus.PASSED and (
                    await self._active_failure_counter.count_active_for_story(access.project_id, story.id) > 0
                    or await self._running_run_checker.has_running_run(access.project_id, story.id)
                ):
                    raise StorySignOffBlockedError
                await self._story_repository.update_test_status(story.id, test_status, actor.user_id, now)
                story = story.model_copy(
                    update={
                        "test_status": test_status,
                        "test_status_changed_at": now,
                        "test_status_changed_by": actor.user_id,
                    }
                )
            sprint = (
                None
                if story.sprint_id is None
                else await self._sprint_repository.find_by_id(access.project_id, story.sprint_id)
            )
            criteria = await self._acceptance_criterion_repository.list_for_story(story.id)
        if is_changing:
            await self._live_event_publisher.publish(
                LiveEvent(
                    type=LiveEventType.STORY_CHANGED,
                    project_id=access.project_id,
                    ids={"storyId": str(story.id), "jiraKey": story.jira_key},
                )
            )
        return build_story_detail(access, story, sprint, criteria)

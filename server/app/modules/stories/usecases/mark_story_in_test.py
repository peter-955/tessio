from datetime import datetime
from uuid import UUID

from app.modules.stories.domains.story.entity import Story
from app.modules.stories.domains.story.repository import StoryRepository
from app.modules.stories.errors import StoryNotFoundError
from app.modules.stories.typing.enums import TestStatus
from app.shared.common import Transaction


class MarkStoryInTestUseCase:
    def __init__(self, transaction: Transaction, story_repository: StoryRepository) -> None:
        self._transaction = transaction
        self._story_repository = story_repository

    async def execute(self, project_id: UUID, story_id: UUID, changed_by: UUID, now: datetime) -> Story:
        async with self._transaction.begin():
            story = await self._story_repository.find_by_id_for_update(project_id, story_id)
            if story is None:
                raise StoryNotFoundError
            if story.test_status is TestStatus.IN_TEST:
                return story
            await self._story_repository.update_test_status(story.id, TestStatus.IN_TEST, changed_by, now)
            return story.model_copy(
                update={
                    "test_status": TestStatus.IN_TEST,
                    "test_status_changed_at": now,
                    "test_status_changed_by": changed_by,
                }
            )

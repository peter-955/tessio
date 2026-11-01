from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.stories.domains.story.entity import Story
from app.modules.stories.domains.story_filter.entity import StoryFilter
from app.modules.stories.domains.story_summary.entity import StorySummary
from app.modules.stories.typing.enums import TestStatus


class StoryRepository(ABC):
    @abstractmethod
    async def find_by_jira_key(self, project_id: UUID, jira_key: str) -> Story | None: ...

    @abstractmethod
    async def find_by_jira_key_for_update(self, project_id: UUID, jira_key: str) -> Story | None: ...

    @abstractmethod
    async def find_by_id_for_update(self, project_id: UUID, story_id: UUID) -> Story | None: ...

    @abstractmethod
    async def list_summaries(self, project_id: UUID, story_filter: StoryFilter) -> list[StorySummary]: ...

    @abstractmethod
    async def save_synced(self, story: Story) -> UUID: ...

    @abstractmethod
    async def update_test_status(
        self, story_id: UUID, test_status: TestStatus, changed_by: UUID, changed_at: datetime
    ) -> None: ...

    @abstractmethod
    async def mark_missing(
        self, project_id: UUID, seen_jira_ids: frozenset[str], sprint_ids: frozenset[UUID], now: datetime
    ) -> int: ...

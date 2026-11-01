from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.gaps.domains.gap_story.entity import GapStory


class GapTargetReader(ABC):
    @abstractmethod
    async def find_story(self, project_id: UUID, jira_key: str) -> GapStory | None: ...

    @abstractmethod
    async def find_criterion_id(self, story_id: UUID, code: str) -> UUID | None: ...

    @abstractmethod
    async def find_test_case_id(self, story_id: UUID, code: str) -> UUID | None: ...

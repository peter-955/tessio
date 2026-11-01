from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.test_cases.domains.case_story.entity import CaseStory


class StoryReader(ABC):
    @abstractmethod
    async def find_by_jira_key(self, project_id: UUID, jira_key: str) -> CaseStory | None: ...

    @abstractmethod
    async def find_by_id(self, project_id: UUID, story_id: UUID) -> CaseStory | None: ...

    @abstractmethod
    async def list_by_jira_keys(self, project_id: UUID, jira_keys: frozenset[str]) -> list[CaseStory]: ...

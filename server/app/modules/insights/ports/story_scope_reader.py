from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.insights.domains.sprint_reference.entity import SprintReference
from app.modules.insights.domains.traced_story.entity import TracedStory


class StoryScopeReader(ABC):
    @abstractmethod
    async def find_story(self, project_id: UUID, jira_key: str) -> TracedStory | None: ...

    @abstractmethod
    async def list_stories(
        self, project_id: UUID, sprint_id: UUID | None, is_excluding_missing: bool
    ) -> list[TracedStory]: ...

    @abstractmethod
    async def find_sprint(self, project_id: UUID, sprint_id: UUID) -> SprintReference | None: ...

    @abstractmethod
    async def find_current_sprint(self, project_id: UUID) -> SprintReference | None: ...

from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.story_context.domains.context_case.entity import ContextCase
from app.modules.story_context.domains.context_criterion.entity import ContextCriterion
from app.modules.story_context.domains.context_environment.entity import ContextEnvironment
from app.modules.story_context.domains.context_story.entity import ContextStory
from app.modules.story_context.domains.data_entry.entity import DataEntry


class StoryContextReader(ABC):
    @abstractmethod
    async def find_story(self, project_id: UUID, jira_key: str) -> ContextStory | None: ...

    @abstractmethod
    async def list_criteria(self, story_id: UUID) -> list[ContextCriterion]: ...

    @abstractmethod
    async def list_ready_cases(self, story_id: UUID) -> list[ContextCase]: ...

    @abstractmethod
    async def count_other_cases(self, story_id: UUID) -> int: ...

    @abstractmethod
    async def list_data_entries(self, project_id: UUID) -> list[DataEntry]: ...

    @abstractmethod
    async def list_environments(self, project_id: UUID) -> list[ContextEnvironment]: ...

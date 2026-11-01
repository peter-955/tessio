from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.runs.domains.run_story.entity import RunStory
from app.modules.runs.domains.story_case.entity import StoryCase
from app.modules.test_data import Environment


class RunTargetReader(ABC):
    @abstractmethod
    async def find_story(self, project_id: UUID, story_key: str) -> RunStory | None: ...

    @abstractmethod
    async def find_story_by_id(self, project_id: UUID, story_id: UUID) -> RunStory | None: ...

    @abstractmethod
    async def list_story_cases(self, project_id: UUID, story_id: UUID) -> list[StoryCase]: ...

    @abstractmethod
    async def find_environment_by_id(self, project_id: UUID, environment_id: UUID) -> Environment | None: ...

    @abstractmethod
    async def list_active_environments(self, project_id: UUID) -> list[Environment]: ...

    @abstractmethod
    async def find_default_environment_id(self, project_id: UUID) -> UUID | None: ...

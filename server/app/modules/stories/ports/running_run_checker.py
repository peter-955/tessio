from abc import ABC, abstractmethod
from uuid import UUID


class RunningRunChecker(ABC):
    @abstractmethod
    async def has_running_run(self, project_id: UUID, story_id: UUID) -> bool: ...

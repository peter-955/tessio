from abc import ABC, abstractmethod
from uuid import UUID


class ActiveFailureCounter(ABC):
    @abstractmethod
    async def count_active_for_story(self, project_id: UUID, story_id: UUID) -> int: ...

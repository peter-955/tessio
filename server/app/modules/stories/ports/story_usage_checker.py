from abc import ABC, abstractmethod
from uuid import UUID


class StoryUsageChecker(ABC):
    @abstractmethod
    async def is_in_use(self, story_id: UUID) -> bool: ...

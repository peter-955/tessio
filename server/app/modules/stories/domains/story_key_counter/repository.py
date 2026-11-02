from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class StoryKeyCounterRepository(ABC):
    @abstractmethod
    async def allocate_number(self, project_id: UUID, now: datetime) -> int: ...

from abc import ABC, abstractmethod
from uuid import UUID


class RunStoryReader(ABC):
    @abstractmethod
    async def find_jira_key(self, story_id: UUID) -> str: ...

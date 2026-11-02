from abc import ABC, abstractmethod
from uuid import UUID


class ReviewPolicyReader(ABC):
    @abstractmethod
    async def is_requiring_separate_reviewer(self, project_id: UUID) -> bool: ...

from abc import ABC, abstractmethod
from uuid import UUID


class FailureAssigneeDirectory(ABC):
    @abstractmethod
    async def is_active_member(self, project_id: UUID, user_id: UUID) -> bool: ...

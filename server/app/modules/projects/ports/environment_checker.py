from abc import ABC, abstractmethod
from uuid import UUID


class EnvironmentChecker(ABC):
    @abstractmethod
    async def is_active_environment(self, project_id: UUID, environment_id: UUID) -> bool: ...

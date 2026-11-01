from abc import ABC, abstractmethod
from uuid import UUID


class EnvironmentUsageChecker(ABC):
    @abstractmethod
    async def is_used_by_runs(self, environment_id: UUID) -> bool: ...

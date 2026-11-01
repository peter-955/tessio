from abc import ABC, abstractmethod
from uuid import UUID


class DataKeyReader(ABC):
    @abstractmethod
    async def list_keys(self, project_id: UUID) -> frozenset[str]: ...

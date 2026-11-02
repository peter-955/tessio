from abc import ABC, abstractmethod
from uuid import UUID


class DataKeyDescriptionRepository(ABC):
    @abstractmethod
    async def find(self, project_id: UUID, key: str) -> str | None: ...

    @abstractmethod
    async def save(self, project_id: UUID, key: str, description: str) -> None: ...

    @abstractmethod
    async def delete(self, project_id: UUID, key: str) -> None: ...

from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.test_data.domains.data_item.entity import DataItem


class DataItemRepository(ABC):
    @abstractmethod
    async def find_by_id(self, project_id: UUID, item_id: UUID) -> DataItem | None: ...

    @abstractmethod
    async def find_by_key(self, project_id: UUID, environment_id: UUID | None, key: str) -> DataItem | None: ...

    @abstractmethod
    async def list_for_environment(self, project_id: UUID, environment_id: UUID | None) -> list[DataItem]: ...

    @abstractmethod
    async def list(self, project_id: UUID) -> list[DataItem]: ...

    @abstractmethod
    async def count_by_key(self, project_id: UUID, key: str) -> int: ...

    @abstractmethod
    async def save(self, item: DataItem) -> None: ...

    @abstractmethod
    async def delete(self, item_id: UUID) -> None: ...

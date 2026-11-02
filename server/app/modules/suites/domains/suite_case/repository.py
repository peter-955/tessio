from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class SuiteCaseRepository(ABC):
    @abstractmethod
    async def list_case_ids(self, suite_id: UUID) -> list[UUID]: ...

    @abstractmethod
    async def replace(self, suite_id: UUID, test_case_ids: list[UUID], now: datetime) -> None: ...

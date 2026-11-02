from abc import ABC, abstractmethod
from collections.abc import Collection
from datetime import datetime
from uuid import UUID

from app.modules.labels.domains.label.entity import Label


class TestCaseLabelRepository(ABC):
    @abstractmethod
    async def list_for_case(self, test_case_id: UUID) -> list[Label]: ...

    @abstractmethod
    async def list_for_cases(self, test_case_ids: Collection[UUID]) -> dict[UUID, list[Label]]: ...

    @abstractmethod
    async def replace_for_case(self, test_case_id: UUID, label_ids: Collection[UUID], linked_at: datetime) -> None: ...

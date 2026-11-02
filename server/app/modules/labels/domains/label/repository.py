from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from app.modules.labels.domains.label.entity import Label
from app.modules.labels.domains.label_summary.entity import LabelSummary


class LabelRepository(ABC):
    @abstractmethod
    async def find_by_id(self, project_id: UUID, label_id: UUID) -> Label | None: ...

    @abstractmethod
    async def find_by_name(self, project_id: UUID, name: str) -> Label | None: ...

    @abstractmethod
    async def list_by_ids(self, project_id: UUID, label_ids: Collection[UUID]) -> list[Label]: ...

    @abstractmethod
    async def list_summaries(self, project_id: UUID) -> list[LabelSummary]: ...

    @abstractmethod
    async def count_cases(self, label_id: UUID) -> int: ...

    @abstractmethod
    async def save(self, label: Label) -> None: ...

    @abstractmethod
    async def delete(self, label_id: UUID) -> None: ...

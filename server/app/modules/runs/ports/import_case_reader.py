from abc import ABC, abstractmethod
from collections.abc import Collection
from uuid import UUID

from app.modules.runs.domains.import_case.entity import ImportCase


class ImportCaseReader(ABC):
    @abstractmethod
    async def list_by_numbers(self, project_id: UUID, numbers: Collection[int]) -> list[ImportCase]: ...

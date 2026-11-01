from abc import ABC, abstractmethod
from uuid import UUID


class ProjectFileTypesReader(ABC):
    @abstractmethod
    async def find_allowed_file_types(self, project_id: UUID) -> list[str]: ...

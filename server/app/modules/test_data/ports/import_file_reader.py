from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.test_data.domains.import_file.entity import ImportFile


class ImportFileReader(ABC):
    @abstractmethod
    async def find(self, project_id: UUID, file_id: UUID, uploaded_by: UUID) -> ImportFile | None: ...

    @abstractmethod
    async def read_content(self, import_file: ImportFile) -> bytes | None: ...

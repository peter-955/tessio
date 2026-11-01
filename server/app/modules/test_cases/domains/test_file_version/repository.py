from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.test_cases.domains.test_file_version_detail.entity import TestFileVersionDetail


class TestFileVersionRepository(ABC):
    @abstractmethod
    async def list_for_file(self, test_file_id: UUID) -> list[TestFileVersionDetail]: ...

    @abstractmethod
    async def exists_for_stored_file(self, stored_file_id: UUID) -> bool: ...

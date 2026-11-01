from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.test_cases.domains.test_file.entity import TestFile
from app.modules.test_cases.domains.test_file_detail.entity import TestFileDetail
from app.modules.test_cases.domains.test_file_version.entity import TestFileVersion


class TestFileRepository(ABC):
    @abstractmethod
    async def list_for_case(self, test_case_id: UUID) -> list[TestFileDetail]: ...

    @abstractmethod
    async def find_by_key(self, test_case_id: UUID, key: str) -> TestFile | None: ...

    @abstractmethod
    async def create(self, test_file: TestFile, version: TestFileVersion) -> None: ...

    @abstractmethod
    async def add_version(self, test_file: TestFile, version: TestFileVersion) -> None: ...

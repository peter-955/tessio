from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion


class TestCaseVersionRepository(ABC):
    @abstractmethod
    async def find_by_id(self, version_id: UUID) -> TestCaseVersion | None: ...

    @abstractmethod
    async def list_for_case(self, test_case_id: UUID) -> list[TestCaseVersion]: ...

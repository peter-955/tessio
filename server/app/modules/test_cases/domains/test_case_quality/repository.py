from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.test_cases.domains.test_case.entity import TestCase


class TestCaseQualityRepository(ABC):
    @abstractmethod
    async def find_by_id_for_update(self, test_case_id: UUID) -> TestCase | None: ...

    @abstractmethod
    async def list_case_ids(self) -> list[UUID]: ...

    @abstractmethod
    async def save(self, test_case: TestCase) -> None: ...

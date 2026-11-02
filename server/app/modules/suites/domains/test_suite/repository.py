from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.suites.domains.test_suite.entity import TestSuite


class TestSuiteRepository(ABC):
    @abstractmethod
    async def find_by_id(self, project_id: UUID, suite_id: UUID) -> TestSuite | None: ...

    @abstractmethod
    async def find_by_id_for_update(self, project_id: UUID, suite_id: UUID) -> TestSuite | None: ...

    @abstractmethod
    async def find_active_by_name(self, project_id: UUID, name: str) -> TestSuite | None: ...

    @abstractmethod
    async def add(self, suite: TestSuite) -> None: ...

    @abstractmethod
    async def save(self, suite: TestSuite) -> None: ...

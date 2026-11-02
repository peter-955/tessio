from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.runs.domains.run_suite.entity import RunSuite
from app.modules.runs.domains.suite_run_case.entity import SuiteRunCase


class SuiteRunScopeReader(ABC):
    @abstractmethod
    async def find_suite(self, project_id: UUID, reference: str) -> RunSuite | None: ...

    @abstractmethod
    async def find_suite_by_id(self, project_id: UUID, suite_id: UUID) -> RunSuite | None: ...

    @abstractmethod
    async def list_suite_cases(self, project_id: UUID, suite_id: UUID) -> list[SuiteRunCase]: ...

from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.runs.domains.run_case.entity import RunCase
from app.modules.runs.domains.run_case_view.entity import RunCaseView


class RunCaseRepository(ABC):
    @abstractmethod
    async def add_all(self, run_cases: list[RunCase]) -> None: ...

    @abstractmethod
    async def list_for_run(self, run_id: UUID) -> list[RunCase]: ...

    @abstractmethod
    async def list_views(self, run_id: UUID) -> list[RunCaseView]: ...

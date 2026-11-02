from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.step_result.entity import StepResult


class CaseResultRepository(ABC):
    @abstractmethod
    async def add(self, case_result: CaseResult, step_results: list[StepResult]) -> None: ...

    @abstractmethod
    async def find_by_id(self, run_id: UUID, case_result_id: UUID) -> CaseResult | None: ...

    @abstractmethod
    async def find_for_case(self, run_id: UUID, test_case_id: UUID, iteration: int = 0) -> CaseResult | None: ...

    @abstractmethod
    async def exists(self, run_id: UUID, test_case_id: UUID, iteration: int = 0) -> bool: ...

    @abstractmethod
    async def list_for_case(self, run_id: UUID, test_case_id: UUID) -> list[CaseResult]: ...

    @abstractmethod
    async def list_for_run(self, run_id: UUID) -> list[CaseResult]: ...

    @abstractmethod
    async def list_steps_for_run(self, run_id: UUID) -> list[StepResult]: ...

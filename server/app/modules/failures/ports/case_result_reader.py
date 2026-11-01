from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.failures.domains.case_result_history_item.entity import CaseResultHistoryItem
from app.modules.failures.domains.failed_step.entity import FailedStep


class CaseResultReader(ABC):
    @abstractmethod
    async def find_failed_step(self, case_result_id: UUID) -> FailedStep | None: ...

    @abstractmethod
    async def list_history(
        self, test_case_id: UUID, since_case_result_id: UUID, limit: int
    ) -> list[CaseResultHistoryItem]: ...

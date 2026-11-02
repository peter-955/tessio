from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.test_cases.domains.decisive_result.entity import DecisiveResult
from app.modules.test_cases.typing.enums import ResultExecutorKind


class CaseResultHistoryReader(ABC):
    @abstractmethod
    async def list_version_results(self, test_case_id: UUID, version_id: UUID, limit: int) -> list[DecisiveResult]: ...

    @abstractmethod
    async def list_results_since(self, test_case_id: UUID, since: datetime, limit: int) -> list[DecisiveResult]: ...

    @abstractmethod
    async def find_latest_per_executor_kind(
        self, test_case_id: UUID, version_id: UUID
    ) -> dict[ResultExecutorKind, DecisiveResult]: ...

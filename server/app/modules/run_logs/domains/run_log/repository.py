from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.run_logs.domains.run_log.entity import RunLog
from app.modules.run_logs.domains.run_log_entry.entity import RunLogEntry


class RunLogRepository(ABC):
    @abstractmethod
    async def replace(self, run_log: RunLog, entries: list[RunLogEntry]) -> None: ...

    @abstractmethod
    async def find(self, run_id: UUID) -> RunLog | None: ...

    @abstractmethod
    async def list_entries(self, run_id: UUID, test_case_id: UUID | None) -> list[RunLogEntry]: ...

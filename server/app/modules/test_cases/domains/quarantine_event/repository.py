from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.test_cases.domains.quarantine_event.entity import QuarantineEvent
from app.modules.test_cases.domains.quarantine_event_view.entity import QuarantineEventView


class QuarantineEventRepository(ABC):
    @abstractmethod
    async def add(self, event: QuarantineEvent) -> None: ...

    @abstractmethod
    async def list_views(self, test_case_id: UUID) -> list[QuarantineEventView]: ...

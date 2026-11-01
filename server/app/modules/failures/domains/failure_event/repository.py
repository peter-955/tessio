from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.failures.domains.failure_event.entity import FailureEvent
from app.modules.failures.domains.failure_event_view.entity import FailureEventView


class FailureEventRepository(ABC):
    @abstractmethod
    async def add(self, event: FailureEvent) -> None: ...

    @abstractmethod
    async def list_views(self, failure_id: UUID) -> list[FailureEventView]: ...

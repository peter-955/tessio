from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.audit.domains.audit_event.entity import AuditEvent


class AuditEventRepository(ABC):
    @abstractmethod
    async def add(self, event: AuditEvent) -> None: ...

    @abstractmethod
    async def list_for_target(self, target_id: UUID) -> list[AuditEvent]: ...

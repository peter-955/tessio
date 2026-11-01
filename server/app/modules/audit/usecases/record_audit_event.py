from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.audit.domains.audit_event.entity import AuditEvent
from app.modules.audit.domains.audit_event.repository import AuditEventRepository
from app.modules.audit.typing.enums import AuditAction
from app.shared.common import Transaction


class RecordAuditEventUseCase:
    def __init__(self, transaction: Transaction, audit_event_repository: AuditEventRepository) -> None:
        self._transaction = transaction
        self._audit_event_repository = audit_event_repository

    async def execute(
        self,
        actor_id: UUID,
        action: AuditAction,
        project_id: UUID | None = None,
        target_id: UUID | None = None,
        api_token_id: UUID | None = None,
        run_id: UUID | None = None,
    ) -> AuditEvent:
        event = AuditEvent(
            id=uuid7(),
            actor_id=actor_id,
            api_token_id=api_token_id,
            project_id=project_id,
            action=action,
            target_id=target_id,
            run_id=run_id,
            created_at=datetime.now(UTC),
        )
        async with self._transaction.begin():
            await self._audit_event_repository.add(event)
        return event

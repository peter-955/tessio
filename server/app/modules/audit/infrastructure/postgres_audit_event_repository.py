from uuid import UUID

from sqlalchemy import select

from app.modules.audit.domains.audit_event.entity import AuditEvent
from app.modules.audit.domains.audit_event.repository import AuditEventRepository
from app.modules.audit.infrastructure.audit_event_table import AuditEventTable
from app.shared.postgres import Database


class PostgresAuditEventRepository(AuditEventRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def add(self, event: AuditEvent) -> None:
        self._database.get_current_session().add(AuditEventTable(**event.model_dump()))

    async def list_for_target(self, target_id: UUID) -> list[AuditEvent]:
        rows = await self._database.get_current_session().scalars(
            select(AuditEventTable)
            .where(AuditEventTable.target_id == target_id)
            .order_by(AuditEventTable.created_at, AuditEventTable.id)
        )
        return [AuditEvent.model_validate(row) for row in rows]

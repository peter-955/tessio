from datetime import datetime
from uuid import UUID

from app.modules.audit.typing.enums import AuditAction
from app.shared.common import Entity


class AuditEvent(Entity):
    id: UUID
    actor_id: UUID
    api_token_id: UUID | None
    project_id: UUID | None
    action: AuditAction
    target_id: UUID | None
    run_id: UUID | None
    created_at: datetime

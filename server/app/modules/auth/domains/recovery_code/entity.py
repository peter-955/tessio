from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class RecoveryCode(Entity):
    id: UUID
    user_id: UUID
    code_hash: str
    used_at: datetime | None
    created_at: datetime

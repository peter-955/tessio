from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class Environment(Entity):
    id: UUID
    project_id: UUID
    name: str
    base_url: str
    health_check_url: str | None
    archived_at: datetime | None
    created_at: datetime

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None

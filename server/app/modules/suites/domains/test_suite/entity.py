from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class TestSuite(Entity):
    id: UUID
    project_id: UUID
    name: str
    description: str | None
    archived_at: datetime | None
    created_by: UUID
    created_at: datetime

    @property
    def is_archived(self) -> bool:
        return self.archived_at is not None

from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class TracedCriterion(Entity):
    id: UUID
    story_id: UUID
    code: str
    position: int
    text: str
    removed_at: datetime | None

    @property
    def is_active(self) -> bool:
        return self.removed_at is None

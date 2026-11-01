from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class AcceptanceCriterion(Entity):
    id: UUID
    story_id: UUID
    position: int
    code: str
    text: str
    removed_at: datetime | None
    created_at: datetime

    @property
    def is_removed(self) -> bool:
        return self.removed_at is not None

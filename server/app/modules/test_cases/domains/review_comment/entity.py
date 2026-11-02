from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class ReviewComment(Entity):
    id: UUID
    test_case_id: UUID
    version_id: UUID
    step_order: int | None
    body: str
    author_id: UUID
    created_at: datetime
    resolved_at: datetime | None
    resolved_by: UUID | None

    @property
    def is_resolved(self) -> bool:
        return self.resolved_at is not None

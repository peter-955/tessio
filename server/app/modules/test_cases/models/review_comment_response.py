from datetime import datetime
from uuid import UUID

from app.shared.common import WireModel


class ReviewCommentResponse(WireModel):
    id: UUID
    version_id: UUID
    version_number: int
    step_order: int | None
    body: str
    author_id: UUID
    author_name: str
    created_at: datetime
    is_resolved: bool
    resolved_at: datetime | None
    resolved_by: UUID | None
    resolved_by_name: str | None

from datetime import datetime
from uuid import UUID

from app.shared.common import WireModel


class EnvironmentResponse(WireModel):
    id: UUID
    name: str
    base_url: str
    health_check_url: str | None
    is_archived: bool
    archived_at: datetime | None
    created_at: datetime

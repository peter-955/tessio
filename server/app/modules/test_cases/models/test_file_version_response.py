from datetime import datetime
from uuid import UUID

from app.shared.common import WireModel


class TestFileVersionResponse(WireModel):
    id: UUID
    number: int
    stored_file_id: UUID
    file_name: str
    content_type: str
    size: int | None
    created_by: UUID
    created_at: datetime

from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class TestFileVersion(Entity):
    id: UUID
    test_file_id: UUID
    number: int
    stored_file_id: UUID
    created_by: UUID
    created_at: datetime

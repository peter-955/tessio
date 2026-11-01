from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class TestFile(Entity):
    id: UUID
    project_id: UUID
    test_case_id: UUID
    key: str
    current_version_id: UUID
    created_by: UUID
    created_at: datetime

from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class RunFile(Entity):
    id: UUID
    run_id: UUID
    test_case_id: UUID
    test_file_version_id: UUID
    key: str
    requested_by: UUID
    created_at: datetime

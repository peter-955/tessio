from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class RunCase(Entity):
    id: UUID
    run_id: UUID
    test_case_id: UUID
    test_case_version_id: UUID
    position: int
    created_at: datetime

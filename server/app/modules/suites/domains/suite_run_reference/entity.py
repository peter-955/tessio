from datetime import datetime
from uuid import UUID

from app.modules.runs import RunStatus
from app.shared.common import Entity


class SuiteRunReference(Entity):
    id: UUID
    status: RunStatus
    started_at: datetime
    finished_at: datetime | None

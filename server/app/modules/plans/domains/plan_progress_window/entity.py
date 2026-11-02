from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class PlanProgressWindow(Entity):
    project_id: UUID
    since: datetime
    until: datetime | None
    environment_id: UUID | None

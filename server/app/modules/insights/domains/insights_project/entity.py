from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class InsightsProject(Entity):
    id: UUID
    created_at: datetime

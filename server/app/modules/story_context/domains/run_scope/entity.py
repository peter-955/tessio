from uuid import UUID

from app.shared.common import Entity


class RunScope(Entity):
    id: UUID
    project_id: UUID
    environment_id: UUID
    started_by: UUID
    is_running: bool

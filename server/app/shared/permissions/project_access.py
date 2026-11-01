from uuid import UUID

from app.shared.common import Entity
from app.shared.permissions.project_role import ProjectRole


class ProjectAccess(Entity):
    project_id: UUID
    project_key: str
    role: ProjectRole | None
    is_archived: bool

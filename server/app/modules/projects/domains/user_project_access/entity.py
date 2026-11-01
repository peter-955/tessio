from uuid import UUID

from app.shared.common import Entity
from app.shared.permissions import ProjectRole


class UserProjectAccess(Entity):
    project_id: UUID
    project_key: str
    project_name: str
    role: ProjectRole
    is_archived: bool

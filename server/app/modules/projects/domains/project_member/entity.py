from datetime import datetime
from uuid import UUID

from app.shared.common import Entity
from app.shared.permissions import ProjectRole


class ProjectMember(Entity):
    id: UUID
    project_id: UUID
    user_id: UUID
    role: ProjectRole
    created_at: datetime

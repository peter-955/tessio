from uuid import UUID

from app.shared.common import Entity
from app.shared.permissions import ProjectRole


class GapAssignee(Entity):
    user_id: UUID
    name: str
    role: ProjectRole

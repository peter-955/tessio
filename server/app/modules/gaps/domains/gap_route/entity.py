from uuid import UUID

from app.shared.common import Entity
from app.shared.permissions import ProjectRole


class GapRoute(Entity):
    assignee_id: UUID | None
    assignee_role: ProjectRole | None

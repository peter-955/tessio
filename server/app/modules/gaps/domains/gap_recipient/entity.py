from uuid import UUID

from app.shared.common import Entity
from app.shared.permissions import ProjectRole


class GapRecipient(Entity):
    user_id: UUID
    role: ProjectRole | None

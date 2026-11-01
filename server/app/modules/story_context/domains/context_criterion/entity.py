from uuid import UUID

from app.shared.common import Entity


class ContextCriterion(Entity):
    id: UUID
    code: str
    text: str
    is_removed: bool

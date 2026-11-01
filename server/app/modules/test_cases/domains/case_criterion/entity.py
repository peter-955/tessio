from uuid import UUID

from app.shared.common import Entity


class CaseCriterion(Entity):
    id: UUID
    story_id: UUID
    code: str
    text: str
    position: int
    is_removed: bool

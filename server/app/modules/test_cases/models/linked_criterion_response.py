from uuid import UUID

from app.shared.common import WireModel


class LinkedCriterionResponse(WireModel):
    id: UUID
    code: str
    text: str
    is_removed: bool

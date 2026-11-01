from uuid import UUID

from app.modules.stories.typing.enums import SprintState
from app.shared.common import WireModel


class SprintReferenceResponse(WireModel):
    id: UUID
    name: str
    state: SprintState

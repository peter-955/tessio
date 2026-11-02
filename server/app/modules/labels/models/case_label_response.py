from uuid import UUID

from app.modules.labels.typing.enums import LabelColor
from app.shared.common import WireModel


class CaseLabelResponse(WireModel):
    id: UUID
    name: str
    color: LabelColor

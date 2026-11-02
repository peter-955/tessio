from datetime import datetime
from uuid import UUID

from app.modules.labels.typing.enums import LabelColor
from app.shared.common import WireModel


class LabelResponse(WireModel):
    id: UUID
    name: str
    color: LabelColor
    case_count: int
    created_at: datetime

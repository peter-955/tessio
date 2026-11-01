from datetime import datetime
from uuid import UUID

from app.modules.test_data.typing.enums import DataItemKind
from app.shared.common import WireModel


class DataItemResponse(WireModel):
    id: UUID
    environment_id: UUID | None
    key: str
    kind: DataItemKind
    value: str | None
    has_value: bool
    created_at: datetime

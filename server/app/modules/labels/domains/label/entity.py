from datetime import datetime
from uuid import UUID

from app.modules.labels.typing.enums import LabelColor
from app.shared.common import Entity


class Label(Entity):
    id: UUID
    project_id: UUID
    name: str
    color: LabelColor
    created_by: UUID
    created_at: datetime

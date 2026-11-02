from datetime import datetime
from uuid import UUID

from app.modules.test_data.typing.enums import DataItemKind
from app.shared.common import Entity


class DataItem(Entity):
    id: UUID
    project_id: UUID
    environment_id: UUID | None
    key: str
    kind: DataItemKind
    value: str | None
    value_encrypted: bytes | None
    created_at: datetime
    description: str | None = None

    @property
    def is_secret(self) -> bool:
        return self.kind is DataItemKind.SECRET

from uuid import UUID

from app.modules.test_data import DataItemKind
from app.shared.common import Entity


class DataEntry(Entity):
    id: UUID
    key: str
    kind: DataItemKind
    value: str | None
    environment_id: UUID | None

    @property
    def is_secret(self) -> bool:
        return self.kind is DataItemKind.SECRET

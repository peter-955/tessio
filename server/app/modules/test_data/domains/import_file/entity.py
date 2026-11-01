from uuid import UUID

from app.shared.common import Entity


class ImportFile(Entity):
    id: UUID
    file_name: str
    object_key: str
    size: int | None
    is_uploaded: bool

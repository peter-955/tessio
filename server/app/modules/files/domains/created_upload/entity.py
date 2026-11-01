from uuid import UUID

from app.shared.common import Entity


class CreatedUpload(Entity):
    file_id: UUID
    url: str
    fields: dict[str, str]
    object_key: str

from uuid import UUID

from app.shared.common import Entity


class AvatarFile(Entity):
    id: UUID
    uploaded_by: UUID
    object_key: str
    file_name: str
    is_uploaded: bool

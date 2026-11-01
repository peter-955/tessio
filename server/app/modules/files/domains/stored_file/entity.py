from datetime import datetime
from uuid import UUID

from app.modules.files.typing.enums import StoredFileKind, StoredFileStatus
from app.shared.common import Entity


class StoredFile(Entity):
    id: UUID
    project_id: UUID | None
    kind: StoredFileKind
    object_key: str
    file_name: str
    content_type: str
    size: int | None
    sha256: str | None
    status: StoredFileStatus
    uploaded_by: UUID
    created_at: datetime

    @property
    def is_uploaded(self) -> bool:
        return self.status is StoredFileStatus.UPLOADED

    @property
    def is_pending(self) -> bool:
        return self.status is StoredFileStatus.PENDING

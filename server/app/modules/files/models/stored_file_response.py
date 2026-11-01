from datetime import datetime
from uuid import UUID

from app.modules.files.typing.enums import StoredFileKind, StoredFileStatus
from app.shared.common import WireModel


class StoredFileResponse(WireModel):
    id: UUID
    kind: StoredFileKind
    file_name: str
    content_type: str
    size: int | None
    status: StoredFileStatus
    created_at: datetime

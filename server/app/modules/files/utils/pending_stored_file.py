from datetime import datetime
from uuid import UUID

from app.modules.files.domains.stored_file.entity import StoredFile
from app.modules.files.typing.enums import StoredFileKind, StoredFileStatus


def build_pending_stored_file(
    file_id: UUID,
    project_id: UUID | None,
    kind: StoredFileKind,
    object_key: str,
    file_name: str,
    content_type: str,
    uploaded_by: UUID,
    now: datetime,
) -> StoredFile:
    return StoredFile(
        id=file_id,
        project_id=project_id,
        kind=kind,
        object_key=object_key,
        file_name=file_name,
        content_type=content_type,
        size=None,
        sha256=None,
        status=StoredFileStatus.PENDING,
        uploaded_by=uploaded_by,
        created_at=now,
    )

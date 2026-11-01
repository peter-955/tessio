from uuid import UUID

from sqlalchemy import select

from app.modules.files import StoredFileKind, StoredFileStatus
from app.modules.files.infrastructure import StoredFileTable
from app.modules.test_data.domains.import_file.entity import ImportFile
from app.modules.test_data.ports.import_file_reader import ImportFileReader
from app.shared.postgres import Database
from app.shared.storage import ObjectStorage


class StorageImportFileReader(ImportFileReader):
    def __init__(self, database: Database, object_storage: ObjectStorage) -> None:
        self._database = database
        self._object_storage = object_storage

    async def find(self, project_id: UUID, file_id: UUID, uploaded_by: UUID) -> ImportFile | None:
        row = await self._database.get_current_session().scalar(
            select(StoredFileTable).where(
                StoredFileTable.id == file_id,
                StoredFileTable.project_id == project_id,
                StoredFileTable.kind == StoredFileKind.IMPORT,
                StoredFileTable.uploaded_by == uploaded_by,
            )
        )
        if row is None:
            return None
        return ImportFile(
            id=row.id,
            file_name=row.file_name,
            object_key=row.object_key,
            size=row.size,
            is_uploaded=row.status is StoredFileStatus.UPLOADED,
        )

    async def read_content(self, import_file: ImportFile) -> bytes | None:
        return await self._object_storage.read_object(import_file.object_key)

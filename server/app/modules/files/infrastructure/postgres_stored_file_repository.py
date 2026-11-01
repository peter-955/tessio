from collections.abc import Collection
from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, select, update

from app.modules.files.domains.stored_file.entity import StoredFile
from app.modules.files.domains.stored_file.repository import StoredFileRepository
from app.modules.files.infrastructure.stored_file_table import StoredFileTable
from app.modules.files.typing.enums import StoredFileStatus
from app.shared.postgres import Database


class PostgresStoredFileRepository(StoredFileRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_id(self, stored_file_id: UUID) -> StoredFile | None:
        row = await self._database.get_current_session().get(StoredFileTable, stored_file_id)
        return None if row is None else StoredFile.model_validate(row)

    async def save(self, stored_file: StoredFile) -> None:
        await self._database.get_current_session().merge(StoredFileTable(**stored_file.model_dump()))

    async def list_pending_created_before(self, cutoff: datetime, limit: int) -> list[StoredFile]:
        rows = await self._database.get_current_session().scalars(
            select(StoredFileTable)
            .where(StoredFileTable.status == StoredFileStatus.PENDING, StoredFileTable.created_at < cutoff)
            .order_by(StoredFileTable.created_at, StoredFileTable.id)
            .limit(limit)
            .with_for_update(skip_locked=True)
        )
        return [StoredFile.model_validate(row) for row in rows]

    async def delete_by_ids(self, stored_file_ids: Collection[UUID]) -> None:
        if not stored_file_ids:
            return
        await self._database.get_current_session().execute(
            delete(StoredFileTable).where(StoredFileTable.id.in_(stored_file_ids))
        )

    async def mark_missing(self, stored_file_ids: Collection[UUID]) -> None:
        if not stored_file_ids:
            return
        await self._database.get_current_session().execute(
            update(StoredFileTable)
            .where(StoredFileTable.id.in_(stored_file_ids))
            .values(status=StoredFileStatus.MISSING)
        )

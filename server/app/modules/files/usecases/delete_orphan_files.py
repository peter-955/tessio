from datetime import datetime

from app.modules.files.domains.stored_file.entity import StoredFile
from app.modules.files.domains.stored_file.repository import StoredFileRepository
from app.modules.files.typing.constants.file_limits import ORPHAN_AGE, ORPHAN_BATCH_SIZE
from app.modules.files.typing.enums import StoredFileKind
from app.shared.common import Transaction
from app.shared.storage import ObjectStorage


class DeleteOrphanFilesUseCase:
    def __init__(
        self, transaction: Transaction, stored_file_repository: StoredFileRepository, object_storage: ObjectStorage
    ) -> None:
        self._transaction = transaction
        self._stored_file_repository = stored_file_repository
        self._object_storage = object_storage

    async def execute(self, now: datetime) -> None:
        cutoff = now - ORPHAN_AGE
        while True:
            async with self._transaction.begin():
                orphan_files = await self._stored_file_repository.list_pending_created_before(cutoff, ORPHAN_BATCH_SIZE)
                await self._handle_batch(orphan_files)
            if len(orphan_files) < ORPHAN_BATCH_SIZE:
                return

    async def _handle_batch(self, orphan_files: list[StoredFile]) -> None:
        screenshot_ids = [orphan.id for orphan in orphan_files if orphan.kind is StoredFileKind.SCREENSHOT]
        deleted_files = [orphan for orphan in orphan_files if orphan.kind is not StoredFileKind.SCREENSHOT]
        for stored_file in deleted_files:
            if await self._object_storage.head_object(stored_file.object_key) is not None:
                await self._object_storage.delete_object(stored_file.object_key)
        await self._stored_file_repository.mark_missing(screenshot_ids)
        await self._stored_file_repository.delete_by_ids([stored_file.id for stored_file in deleted_files])

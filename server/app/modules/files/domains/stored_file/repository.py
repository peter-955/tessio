from abc import ABC, abstractmethod
from collections.abc import Collection
from datetime import datetime
from uuid import UUID

from app.modules.files.domains.stored_file.entity import StoredFile


class StoredFileRepository(ABC):
    @abstractmethod
    async def find_by_id(self, stored_file_id: UUID) -> StoredFile | None: ...

    @abstractmethod
    async def save(self, stored_file: StoredFile) -> None: ...

    @abstractmethod
    async def list_pending_created_before(self, cutoff: datetime, limit: int) -> list[StoredFile]: ...

    @abstractmethod
    async def delete_by_ids(self, stored_file_ids: Collection[UUID]) -> None: ...

    @abstractmethod
    async def mark_missing(self, stored_file_ids: Collection[UUID]) -> None: ...

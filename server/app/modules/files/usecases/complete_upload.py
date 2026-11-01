from uuid import UUID

from app.modules.files.domains.stored_file.entity import StoredFile
from app.modules.files.domains.stored_file.repository import StoredFileRepository
from app.modules.files.errors import (
    FileTooLargeError,
    FileTypeNotAllowedError,
    StoredFileNotFoundError,
    UnsupportedUploadKindError,
    UploadNotCompletedError,
)
from app.modules.files.typing.constants.file_limits import MAX_AVATAR_BYTES, MAX_FILE_BYTES
from app.modules.files.typing.constants.upload_capability import UPLOAD_CAPABILITY_BY_KIND, UPLOAD_KIND_BY_FILE_KIND
from app.modules.files.typing.enums import StoredFileKind, StoredFileStatus
from app.modules.files.utils.content_type import normalize_content_type
from app.shared.common import Transaction
from app.shared.permissions import Actor, ProjectAccessResolver, require, require_any
from app.shared.storage import ObjectStorage


class CompleteUploadUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        stored_file_repository: StoredFileRepository,
        object_storage: ObjectStorage,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._stored_file_repository = stored_file_repository
        self._object_storage = object_storage

    async def execute(self, actor: Actor, file_id: UUID, project_key: str | None) -> StoredFile:
        async with self._transaction.begin():
            stored_file = await self._find_own_file(actor, file_id, project_key)
            if stored_file.is_uploaded:
                return stored_file
            if not stored_file.is_pending:
                raise StoredFileNotFoundError
            uploaded_file = await self._confirm_uploaded_object(stored_file)
            await self._stored_file_repository.save(uploaded_file)
        return uploaded_file

    async def _find_own_file(self, actor: Actor, file_id: UUID, project_key: str | None) -> StoredFile:
        if project_key is None:
            stored_file = await self._stored_file_repository.find_by_id(file_id)
            if (
                stored_file is None
                or stored_file.uploaded_by != actor.user_id
                or stored_file.project_id is not None
                or stored_file.kind is not StoredFileKind.AVATAR
            ):
                raise StoredFileNotFoundError
            return stored_file
        access = await self._project_access_resolver.resolve(actor, project_key)
        require_any(access, UPLOAD_CAPABILITY_BY_KIND.values())
        stored_file = await self._stored_file_repository.find_by_id(file_id)
        if (
            stored_file is None
            or stored_file.uploaded_by != actor.user_id
            or stored_file.project_id != access.project_id
        ):
            raise StoredFileNotFoundError
        upload_kind = UPLOAD_KIND_BY_FILE_KIND.get(stored_file.kind)
        if upload_kind is None:
            raise UnsupportedUploadKindError
        require(access, UPLOAD_CAPABILITY_BY_KIND[upload_kind])
        return stored_file

    async def _confirm_uploaded_object(self, stored_file: StoredFile) -> StoredFile:
        max_bytes = MAX_AVATAR_BYTES if stored_file.kind is StoredFileKind.AVATAR else MAX_FILE_BYTES
        head = await self._object_storage.head_object(stored_file.object_key)
        if head is None:
            raise UploadNotCompletedError
        if head.size > max_bytes:
            await self._object_storage.delete_object(stored_file.object_key)
            raise FileTooLargeError
        content_type = normalize_content_type(head.content_type)
        if content_type != stored_file.content_type:
            await self._object_storage.delete_object(stored_file.object_key)
            raise FileTypeNotAllowedError
        return stored_file.model_copy(
            update={"size": head.size, "content_type": content_type, "status": StoredFileStatus.UPLOADED}
        )

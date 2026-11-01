from datetime import UTC, datetime
from uuid import uuid7

from app.modules.files.domains.created_upload.entity import CreatedUpload
from app.modules.files.domains.stored_file.repository import StoredFileRepository
from app.modules.files.errors import FileTooLargeError, FileTypeNotAllowedError
from app.modules.files.ports.project_file_types_reader import ProjectFileTypesReader
from app.modules.files.typing.constants.file_limits import MAX_FILE_BYTES, SCREENSHOT_CONTENT_TYPES, UPLOAD_LIFETIME
from app.modules.files.typing.constants.upload_capability import UPLOAD_CAPABILITY_BY_KIND
from app.modules.files.typing.enums import StoredFileKind, UploadKind
from app.modules.files.utils.content_type import normalize_content_type
from app.modules.files.utils.created_upload import build_created_upload
from app.modules.files.utils.file_name import sanitize_file_name
from app.modules.files.utils.object_key import build_object_key
from app.modules.files.utils.pending_stored_file import build_pending_stored_file
from app.shared.common import Transaction
from app.shared.permissions import Actor, ProjectAccessResolver, require
from app.shared.storage import ObjectStorage


class CreateUploadUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        stored_file_repository: StoredFileRepository,
        project_file_types_reader: ProjectFileTypesReader,
        object_storage: ObjectStorage,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._stored_file_repository = stored_file_repository
        self._project_file_types_reader = project_file_types_reader
        self._object_storage = object_storage

    async def execute(
        self, actor: Actor, project_key: str, kind: UploadKind, file_name: str, content_type: str, size: int
    ) -> CreatedUpload:
        normalized_content_type = normalize_content_type(content_type)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, UPLOAD_CAPABILITY_BY_KIND[kind])
            if not 1 <= size <= MAX_FILE_BYTES:
                raise FileTooLargeError
            allowed_file_types = {
                normalize_content_type(file_type)
                for file_type in await self._project_file_types_reader.find_allowed_file_types(access.project_id)
            }
            if kind is UploadKind.EVIDENCE:
                allowed_file_types |= SCREENSHOT_CONTENT_TYPES
            if normalized_content_type not in allowed_file_types:
                raise FileTypeNotAllowedError
            file_id = uuid7()
            stored_file_kind = StoredFileKind(kind.value)
            stored_file = build_pending_stored_file(
                file_id,
                access.project_id,
                stored_file_kind,
                build_object_key(access.project_id, stored_file_kind, file_id, sanitize_file_name(file_name)),
                file_name,
                normalized_content_type,
                actor.user_id,
                datetime.now(UTC),
            )
            await self._stored_file_repository.save(stored_file)
        signed_upload = self._object_storage.create_signed_object_upload(
            stored_file.object_key,
            MAX_FILE_BYTES,
            UPLOAD_LIFETIME,
            normalized_content_type,
        )
        return build_created_upload(stored_file, signed_upload)

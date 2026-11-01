from datetime import UTC, datetime
from uuid import uuid7

from app.modules.files.domains.created_upload.entity import CreatedUpload
from app.modules.files.domains.stored_file.repository import StoredFileRepository
from app.modules.files.errors import FileTooLargeError, FileTypeNotAllowedError
from app.modules.files.typing.constants.file_limits import AVATAR_CONTENT_TYPES, MAX_AVATAR_BYTES, UPLOAD_LIFETIME
from app.modules.files.typing.enums import StoredFileKind
from app.modules.files.utils.content_type import normalize_content_type
from app.modules.files.utils.created_upload import build_created_upload
from app.modules.files.utils.file_name import sanitize_file_name
from app.modules.files.utils.object_key import build_avatar_object_key
from app.modules.files.utils.pending_stored_file import build_pending_stored_file
from app.shared.common import Transaction
from app.shared.permissions import Actor
from app.shared.storage import ObjectStorage


class CreateAvatarUploadUseCase:
    def __init__(
        self, transaction: Transaction, stored_file_repository: StoredFileRepository, object_storage: ObjectStorage
    ) -> None:
        self._transaction = transaction
        self._stored_file_repository = stored_file_repository
        self._object_storage = object_storage

    async def execute(self, actor: Actor, file_name: str, content_type: str, size: int) -> CreatedUpload:
        normalized_content_type = normalize_content_type(content_type)
        if not 1 <= size <= MAX_AVATAR_BYTES:
            raise FileTooLargeError
        if normalized_content_type not in AVATAR_CONTENT_TYPES:
            raise FileTypeNotAllowedError
        file_id = uuid7()
        stored_file = build_pending_stored_file(
            file_id,
            None,
            StoredFileKind.AVATAR,
            build_avatar_object_key(actor.user_id, file_id, sanitize_file_name(file_name)),
            file_name,
            normalized_content_type,
            actor.user_id,
            datetime.now(UTC),
        )
        async with self._transaction.begin():
            await self._stored_file_repository.save(stored_file)
        signed_upload = self._object_storage.create_signed_object_upload(
            stored_file.object_key,
            MAX_AVATAR_BYTES,
            UPLOAD_LIFETIME,
            normalized_content_type,
        )
        return build_created_upload(stored_file, signed_upload)

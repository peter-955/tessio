from datetime import UTC, datetime
from uuid import UUID

from app.modules.files.domains.download_link.entity import DownloadLink
from app.modules.files.domains.stored_file.repository import StoredFileRepository
from app.modules.files.errors import StoredFileNotFoundError
from app.modules.files.typing.constants.downloadable_file_kind import DOWNLOADABLE_FILE_KINDS
from app.modules.files.typing.constants.file_limits import DOWNLOAD_LINK_LIFETIME
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require
from app.shared.storage import ObjectStorage


class CreateDownloadLinkUseCase:
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

    async def execute(self, actor: Actor, project_key: str, file_id: UUID) -> DownloadLink:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.FILE_DOWNLOAD)
            stored_file = await self._stored_file_repository.find_by_id(file_id)
        if (
            stored_file is None
            or stored_file.project_id != access.project_id
            or stored_file.kind not in DOWNLOADABLE_FILE_KINDS
            or not stored_file.is_uploaded
        ):
            raise StoredFileNotFoundError
        url = self._object_storage.create_signed_download(
            stored_file.object_key, DOWNLOAD_LINK_LIFETIME, stored_file.file_name
        )
        return DownloadLink(url=url, expires_at=datetime.now(UTC) + DOWNLOAD_LINK_LIFETIME)

from uuid import UUID

from app.modules.auth.errors import AvatarNotFoundError
from app.modules.auth.ports.avatar_file_reader import AvatarFileReader
from app.modules.auth.typing.constants.user_management import AVATAR_LINK_LIFETIME
from app.modules.users import UserRepository
from app.shared.common import Transaction
from app.shared.storage import ObjectStorage


class GetAvatarLinkUseCase:
    def __init__(
        self,
        transaction: Transaction,
        user_repository: UserRepository,
        avatar_file_reader: AvatarFileReader,
        object_storage: ObjectStorage,
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._avatar_file_reader = avatar_file_reader
        self._object_storage = object_storage

    async def execute(self, user_id: UUID) -> str:
        async with self._transaction.begin():
            user = await self._user_repository.find_by_id(user_id)
            if user is None or user.avatar_file_id is None:
                raise AvatarNotFoundError
            avatar_file = await self._avatar_file_reader.find(user.avatar_file_id)
        if avatar_file is None or not avatar_file.is_uploaded:
            raise AvatarNotFoundError
        return self._object_storage.create_signed_download(
            avatar_file.object_key, AVATAR_LINK_LIFETIME, avatar_file.file_name
        )

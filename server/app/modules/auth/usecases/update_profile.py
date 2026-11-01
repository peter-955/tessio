from uuid import UUID

from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.domains.profile_changes.entity import ProfileChanges
from app.modules.auth.errors import AvatarNotFoundError, UploadNotCompletedError
from app.modules.auth.ports.avatar_file_reader import AvatarFileReader
from app.modules.auth.utils.active_user import lock_active_user
from app.modules.auth.utils.profile_changes import apply_profile_changes
from app.modules.users import User, UserRepository
from app.shared.common import Transaction


class UpdateProfileUseCase:
    def __init__(
        self, transaction: Transaction, user_repository: UserRepository, avatar_file_reader: AvatarFileReader
    ) -> None:
        self._transaction = transaction
        self._user_repository = user_repository
        self._avatar_file_reader = avatar_file_reader

    async def execute(self, authenticated: AuthenticatedSession, changes: ProfileChanges) -> User:
        async with self._transaction.begin():
            user = await lock_active_user(self._user_repository, authenticated.user.id)
            if changes.is_avatar_changed and changes.avatar_file_id is not None:
                await self._ensure_avatar_is_usable(user, changes.avatar_file_id)
            updated_user = apply_profile_changes(user, changes)
            await self._user_repository.update(user, updated_user)
        return updated_user

    async def _ensure_avatar_is_usable(self, user: User, avatar_file_id: UUID) -> None:
        avatar_file = await self._avatar_file_reader.find(avatar_file_id)
        if avatar_file is None or avatar_file.uploaded_by != user.id:
            raise AvatarNotFoundError
        if not avatar_file.is_uploaded:
            raise UploadNotCompletedError

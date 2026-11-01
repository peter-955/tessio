from uuid import UUID

from app.modules.auth.errors import NotSignedInError
from app.modules.users import User, UserRepository, UserStatus


async def lock_active_user(user_repository: UserRepository, user_id: UUID) -> User:
    user = await user_repository.find_by_id_for_update(user_id)
    if user is None or user.status is not UserStatus.ACTIVE:
        raise NotSignedInError
    return user

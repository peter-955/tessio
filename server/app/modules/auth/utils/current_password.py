from app.modules.auth.errors import InvalidCurrentPasswordError
from app.modules.auth.ports.password_hasher import PasswordHasher
from app.modules.users import User


async def ensure_current_password(password_hasher: PasswordHasher, user: User, password: str) -> None:
    if user.password_hash is None or not await password_hasher.verify_password(user.password_hash, password):
        raise InvalidCurrentPasswordError

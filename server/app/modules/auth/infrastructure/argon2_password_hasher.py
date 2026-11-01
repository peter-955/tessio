import asyncio

from argon2 import PasswordHasher as Argon2Hasher
from argon2.exceptions import VerifyMismatchError

from app.modules.auth.ports.password_hasher import PasswordHasher


class Argon2PasswordHasher(PasswordHasher):
    def __init__(self) -> None:
        self._hasher = Argon2Hasher()

    async def hash_password(self, password: str) -> str:
        return await asyncio.to_thread(self._hasher.hash, password)

    async def verify_password(self, password_hash: str, password: str) -> bool:
        return await asyncio.to_thread(self._verify_password_blocking, password_hash, password)

    def _verify_password_blocking(self, password_hash: str, password: str) -> bool:
        try:
            return self._hasher.verify(password_hash, password)
        except VerifyMismatchError:
            return False

from abc import ABC, abstractmethod


class PasswordHasher(ABC):
    @abstractmethod
    async def hash_password(self, password: str) -> str: ...

    @abstractmethod
    async def verify_password(self, password_hash: str, password: str) -> bool: ...

from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.auth.domains.recovery_code.entity import RecoveryCode


class RecoveryCodeRepository(ABC):
    @abstractmethod
    async def replace_for_user(self, user_id: UUID, recovery_codes: list[RecoveryCode]) -> None: ...

    @abstractmethod
    async def find_unused(self, user_id: UUID, code_hash: str) -> RecoveryCode | None: ...

    @abstractmethod
    async def save(self, recovery_code: RecoveryCode) -> None: ...

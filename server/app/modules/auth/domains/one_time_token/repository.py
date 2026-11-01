from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.auth.domains.one_time_token.entity import OneTimeToken
from app.modules.auth.typing.enums import OneTimeTokenPurpose


class OneTimeTokenRepository(ABC):
    @abstractmethod
    async def find_by_token_hash(self, token_hash: str, purpose: OneTimeTokenPurpose) -> OneTimeToken | None: ...

    @abstractmethod
    async def save(self, one_time_token: OneTimeToken) -> None: ...

    @abstractmethod
    async def expire_unused_for_user(self, user_id: UUID, purpose: OneTimeTokenPurpose, now: datetime) -> None: ...

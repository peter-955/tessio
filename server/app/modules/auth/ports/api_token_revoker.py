from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID


class ApiTokenRevoker(ABC):
    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID, now: datetime) -> None: ...

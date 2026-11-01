from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.auth.domains.user_session.entity import UserSession


class UserSessionRepository(ABC):
    @abstractmethod
    async def find_by_token_hash(self, token_hash: str) -> UserSession | None: ...

    @abstractmethod
    async def save(self, user_session: UserSession) -> None: ...

    @abstractmethod
    async def delete(self, user_session_id: UUID) -> None: ...

    @abstractmethod
    async def delete_all_for_user(self, user_id: UUID) -> None: ...

    @abstractmethod
    async def delete_all_for_user_except(self, user_id: UUID, kept_user_session_id: UUID) -> None: ...

    @abstractmethod
    async def delete_expired(self, now: datetime) -> int: ...

from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.api_tokens.domains.api_token.entity import ApiToken
from app.modules.api_tokens.domains.api_token_summary.entity import ApiTokenSummary


class ApiTokenRepository(ABC):
    @abstractmethod
    async def find_by_token_hash(self, token_hash: str) -> ApiToken | None: ...

    @abstractmethod
    async def find_by_id(self, token_id: UUID) -> ApiToken | None: ...

    @abstractmethod
    async def count_active_for_user(self, user_id: UUID, now: datetime) -> int: ...

    @abstractmethod
    async def list_summaries_for_user(self, user_id: UUID) -> list[ApiTokenSummary]: ...

    @abstractmethod
    async def save(self, api_token: ApiToken) -> None: ...

    @abstractmethod
    async def revoke_all_for_user(self, user_id: UUID, now: datetime) -> None: ...

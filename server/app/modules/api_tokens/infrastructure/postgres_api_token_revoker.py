from datetime import datetime
from uuid import UUID

from app.modules.api_tokens.infrastructure.postgres_api_token_repository import PostgresApiTokenRepository
from app.modules.auth.ports.api_token_revoker import ApiTokenRevoker
from app.shared.postgres import Database


class PostgresApiTokenRevoker(ApiTokenRevoker):
    def __init__(self, database: Database) -> None:
        self._api_token_repository = PostgresApiTokenRepository(database)

    async def revoke_all_for_user(self, user_id: UUID, now: datetime) -> None:
        await self._api_token_repository.revoke_all_for_user(user_id, now)

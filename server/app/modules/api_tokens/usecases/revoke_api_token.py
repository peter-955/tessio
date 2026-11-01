from datetime import UTC, datetime
from uuid import UUID

from app.modules.api_tokens.domains.api_token.repository import ApiTokenRepository
from app.modules.api_tokens.errors import ApiTokenNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor


class RevokeApiTokenUseCase:
    def __init__(self, transaction: Transaction, api_token_repository: ApiTokenRepository) -> None:
        self._transaction = transaction
        self._api_token_repository = api_token_repository

    async def execute(self, actor: Actor, token_id: UUID) -> None:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            api_token = await self._api_token_repository.find_by_id(token_id)
            if api_token is None or api_token.user_id != actor.user_id:
                raise ApiTokenNotFoundError
            if api_token.revoked_at is None:
                await self._api_token_repository.save(api_token.model_copy(update={"revoked_at": now}))

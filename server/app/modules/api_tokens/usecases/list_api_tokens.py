from app.modules.api_tokens.domains.api_token.repository import ApiTokenRepository
from app.modules.api_tokens.domains.api_token_summary.entity import ApiTokenSummary
from app.shared.common import Transaction
from app.shared.permissions import Actor


class ListApiTokensUseCase:
    def __init__(self, transaction: Transaction, api_token_repository: ApiTokenRepository) -> None:
        self._transaction = transaction
        self._api_token_repository = api_token_repository

    async def execute(self, actor: Actor) -> list[ApiTokenSummary]:
        async with self._transaction.begin():
            return await self._api_token_repository.list_summaries_for_user(actor.user_id)

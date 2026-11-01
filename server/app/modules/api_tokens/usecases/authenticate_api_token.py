from datetime import UTC, datetime

from app.modules.api_tokens.domains.api_token.repository import ApiTokenRepository
from app.modules.api_tokens.errors import InvalidApiTokenError
from app.modules.api_tokens.typing.constants import API_CREDENTIAL_START, LAST_USED_REFRESH_INTERVAL
from app.modules.api_tokens.utils.api_token_secret import hash_api_token
from app.modules.users import UserRepository, UserStatus, build_actor
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class AuthenticateApiTokenUseCase:
    def __init__(
        self,
        transaction: Transaction,
        api_token_repository: ApiTokenRepository,
        user_repository: UserRepository,
        project_access_resolver: ProjectAccessResolver,
    ) -> None:
        self._transaction = transaction
        self._api_token_repository = api_token_repository
        self._user_repository = user_repository
        self._project_access_resolver = project_access_resolver

    async def execute(self, token: str, capability: Capability) -> Actor:
        if not token.startswith(API_CREDENTIAL_START):
            raise InvalidApiTokenError
        now = datetime.now(UTC)
        async with self._transaction.begin():
            api_token = await self._api_token_repository.find_by_token_hash(hash_api_token(token))
            if api_token is None or not api_token.is_active(now):
                raise InvalidApiTokenError
            user = await self._user_repository.find_by_id(api_token.user_id)
            if user is None or user.status != UserStatus.ACTIVE:
                raise InvalidApiTokenError
            actor = build_actor(user).model_copy(
                update={"api_token_id": api_token.id, "token_project_id": api_token.project_id}
            )
            try:
                access = await self._project_access_resolver.resolve_by_id(actor, api_token.project_id)
            except ProjectNotFoundError as error:
                raise InvalidApiTokenError from error
            if access.role is None:
                raise InvalidApiTokenError
            require(access, capability)
            if api_token.last_used_at is None or now - api_token.last_used_at >= LAST_USED_REFRESH_INTERVAL:
                await self._api_token_repository.save(api_token.model_copy(update={"last_used_at": now}))
        return actor

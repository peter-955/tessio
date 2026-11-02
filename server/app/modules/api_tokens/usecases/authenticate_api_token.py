from datetime import UTC, datetime

from app.modules.api_tokens.domains.api_token.entity import ApiToken
from app.modules.api_tokens.domains.api_token.repository import ApiTokenRepository
from app.modules.api_tokens.errors import InvalidApiTokenError, TokenScopeNotAllowedError
from app.modules.api_tokens.typing.constants import API_CREDENTIAL_START
from app.modules.api_tokens.typing.enums import ApiTokenScope
from app.modules.api_tokens.utils.api_token_secret import hash_api_token
from app.modules.api_tokens.utils.api_token_usage import build_usage_update, read_storable_plugin_version
from app.modules.api_tokens.utils.bearer_token import read_bearer_token
from app.modules.auth import BearerTokenScopeGate, NotSignedInError
from app.modules.plugin import CheckPluginVersionUseCase
from app.modules.users import UserRepository, UserStatus, build_actor
from app.shared.common import Transaction
from app.shared.permissions import (
    Actor,
    Capability,
    ProjectAccess,
    ProjectAccessResolver,
    ProjectNotFoundError,
    require,
)


class AuthenticateApiTokenUseCase(BearerTokenScopeGate):
    def __init__(
        self,
        transaction: Transaction,
        api_token_repository: ApiTokenRepository,
        user_repository: UserRepository,
        project_access_resolver: ProjectAccessResolver,
        check_plugin_version: CheckPluginVersionUseCase,
    ) -> None:
        self._transaction = transaction
        self._check_plugin_version = check_plugin_version
        self._api_token_repository = api_token_repository
        self._user_repository = user_repository
        self._project_access_resolver = project_access_resolver

    async def execute_for_mcp(self, token: str, capability: Capability, plugin_version: str | None) -> Actor:
        actor, access = await self._authenticate(
            token, read_storable_plugin_version(plugin_version), ApiTokenScope.MCP, TokenScopeNotAllowedError
        )
        self._check_plugin_version.execute(plugin_version)
        require(access, capability)
        return actor

    async def execute(self, token: str, capability: Capability) -> Actor:
        actor, access = await self._authenticate(token, None, ApiTokenScope.MCP, TokenScopeNotAllowedError)
        require(access, capability)
        return actor

    async def execute_for_rest(self, token: str, project_key: str) -> Actor:
        actor, access = await self._authenticate(token, None, ApiTokenScope.API, NotSignedInError)
        async with self._transaction.begin():
            path_access = await self._project_access_resolver.resolve(actor, project_key)
        if path_access.project_id != access.project_id:
            raise ProjectNotFoundError
        return actor

    async def refuse_on_session_route(self, authorization: str) -> None:
        token = read_bearer_token(authorization)
        if token is None or not token.startswith(API_CREDENTIAL_START):
            return
        now = datetime.now(UTC)
        async with self._transaction.begin():
            api_token = await self._api_token_repository.find_by_token_hash(hash_api_token(token))
        if api_token is not None and api_token.is_active(now) and api_token.scope is ApiTokenScope.API:
            raise TokenScopeNotAllowedError

    async def _authenticate(
        self,
        token: str,
        plugin_version: str | None,
        scope: ApiTokenScope,
        scope_error: type[Exception],
    ) -> tuple[Actor, ProjectAccess]:
        if not token.startswith(API_CREDENTIAL_START):
            raise InvalidApiTokenError
        now = datetime.now(UTC)
        async with self._transaction.begin():
            api_token = await self._api_token_repository.find_by_token_hash(hash_api_token(token))
            if api_token is None or not api_token.is_active(now):
                raise InvalidApiTokenError
            self._ensure_scope(api_token, scope, scope_error)
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
            usage_update = build_usage_update(api_token, now, plugin_version)
            if usage_update:
                await self._api_token_repository.save(api_token.model_copy(update=usage_update))
        return actor, access

    @staticmethod
    def _ensure_scope(api_token: ApiToken, scope: ApiTokenScope, scope_error: type[Exception]) -> None:
        if api_token.scope is not scope:
            raise scope_error

from datetime import UTC, datetime, timedelta
from uuid import uuid7

from app.modules.api_tokens.domains.api_token.entity import ApiToken
from app.modules.api_tokens.domains.api_token.repository import ApiTokenRepository
from app.modules.api_tokens.domains.api_token_summary.entity import ApiTokenSummary
from app.modules.api_tokens.domains.created_api_token.entity import CreatedApiToken
from app.modules.api_tokens.errors import ProjectMembershipRequiredError, TokenLimitReachedError
from app.modules.api_tokens.typing.constants import MAXIMUM_ACTIVE_API_TOKENS
from app.modules.api_tokens.utils.api_token_secret import generate_api_token, hash_api_token
from app.modules.projects.domains.project.repository import ProjectRepository
from app.modules.projects.domains.project_member.repository import ProjectMemberRepository
from app.shared.common import Transaction
from app.shared.permissions import (
    Actor,
    Capability,
    PermissionDeniedError,
    ProjectAccessResolver,
    ProjectNotFoundError,
    require,
)


class CreateApiTokenUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        project_repository: ProjectRepository,
        project_member_repository: ProjectMemberRepository,
        api_token_repository: ApiTokenRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._project_repository = project_repository
        self._project_member_repository = project_member_repository
        self._api_token_repository = api_token_repository

    async def execute(self, actor: Actor, project_key: str, name: str, lifetime_days: int) -> CreatedApiToken:
        if actor.api_token_id is not None:
            raise PermissionDeniedError
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.API_TOKEN_CREATE)
            if await self._project_member_repository.find(access.project_id, actor.user_id) is None:
                raise ProjectMembershipRequiredError
            if await self._api_token_repository.count_active_for_user(actor.user_id, now) >= MAXIMUM_ACTIVE_API_TOKENS:
                raise TokenLimitReachedError
            project = await self._project_repository.find_by_id(access.project_id)
            if project is None:
                raise ProjectNotFoundError
            token, prefix = generate_api_token()
            api_token = ApiToken(
                id=uuid7(),
                user_id=actor.user_id,
                project_id=access.project_id,
                name=name,
                prefix=prefix,
                token_hash=hash_api_token(token),
                expires_at=now + timedelta(days=lifetime_days),
                last_used_at=None,
                revoked_at=None,
                created_at=now,
            )
            await self._api_token_repository.save(api_token)
        return CreatedApiToken(
            token=token,
            summary=ApiTokenSummary(api_token=api_token, project_key=access.project_key, project_name=project.name),
        )

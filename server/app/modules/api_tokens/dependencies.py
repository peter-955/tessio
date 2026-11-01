from typing import Annotated

from fastapi import Depends, Request

from app.modules.api_tokens.errors import InvalidApiTokenError
from app.modules.api_tokens.usecases.authenticate_api_token import AuthenticateApiTokenUseCase
from app.modules.api_tokens.usecases.create_api_token import CreateApiTokenUseCase
from app.modules.api_tokens.usecases.list_api_tokens import ListApiTokensUseCase
from app.modules.api_tokens.usecases.revoke_api_token import RevokeApiTokenUseCase
from app.modules.api_tokens.utils.bearer_token import read_bearer_token
from app.shared.permissions import Actor, Capability


def get_create_api_token(request: Request) -> CreateApiTokenUseCase:
    use_case: CreateApiTokenUseCase = request.app.state.container.create_api_token
    return use_case


def get_list_api_tokens(request: Request) -> ListApiTokensUseCase:
    use_case: ListApiTokensUseCase = request.app.state.container.list_api_tokens
    return use_case


def get_revoke_api_token(request: Request) -> RevokeApiTokenUseCase:
    use_case: RevokeApiTokenUseCase = request.app.state.container.revoke_api_token
    return use_case


def get_authenticate_api_token(request: Request) -> AuthenticateApiTokenUseCase:
    use_case: AuthenticateApiTokenUseCase = request.app.state.container.authenticate_api_token
    return use_case


class ApiTokenActorDependency:
    def __init__(self, capability: Capability) -> None:
        self._capability = capability

    async def __call__(
        self,
        request: Request,
        use_case: Annotated[AuthenticateApiTokenUseCase, Depends(get_authenticate_api_token)],
    ) -> Actor:
        token = read_bearer_token(request.headers.get("authorization", ""))
        if token is None:
            raise InvalidApiTokenError
        return await use_case.execute(token, self._capability)


def get_api_token_actor(capability: Capability) -> ApiTokenActorDependency:
    return ApiTokenActorDependency(capability)

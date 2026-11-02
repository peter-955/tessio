from collections.abc import Mapping

from app.modules.api_tokens.errors import InvalidApiTokenError
from app.modules.api_tokens.usecases.authenticate_api_token import AuthenticateApiTokenUseCase
from app.modules.api_tokens.utils.bearer_token import read_bearer_token
from app.modules.plugin import PLUGIN_VERSION_HEADER
from app.shared.permissions import Actor, Capability


async def authenticate_mcp_api_token(
    headers: Mapping[str, str] | None, use_case: AuthenticateApiTokenUseCase, capability: Capability
) -> Actor:
    request_headers = headers or {}
    token = read_bearer_token(request_headers.get("authorization", ""))
    if token is None:
        raise InvalidApiTokenError
    return await use_case.execute_for_mcp(token, capability, request_headers.get(PLUGIN_VERSION_HEADER))

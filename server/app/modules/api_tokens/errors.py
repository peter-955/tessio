from app.modules.api_tokens.typing.constants import MAXIMUM_ACTIVE_API_TOKENS
from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class InvalidApiTokenError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_API_TOKEN, "The API token is invalid, expired or revoked.")


class TokenLimitReachedError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.TOKEN_LIMIT_REACHED,
            f"You already have {MAXIMUM_ACTIVE_API_TOKENS} active tokens. Revoke one first.",
        )


class ProjectMembershipRequiredError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.PERMISSION_DENIED, "Only project members can create a token for this project.")


class TokenScopeNotAllowedError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.TOKEN_SCOPE_NOT_ALLOWED,
            "This token's scope does not allow this request. Use an mcp token for Claude Code "
            "and an api token for the public REST routes.",
        )


class ApiTokenNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Token not found.")

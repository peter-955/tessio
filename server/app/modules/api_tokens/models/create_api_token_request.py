from typing import Annotated

from pydantic import Field, StringConstraints

from app.modules.api_tokens.typing.constants import (
    DEFAULT_API_TOKEN_LIFETIME_DAYS,
    MAXIMUM_API_TOKEN_LIFETIME_DAYS,
    MAXIMUM_API_TOKEN_NAME_LENGTH,
)
from app.modules.api_tokens.typing.enums import ApiTokenScope
from app.shared.common import WireModel


class CreateApiTokenRequest(WireModel):
    name: Annotated[
        str, StringConstraints(strip_whitespace=True, min_length=1, max_length=MAXIMUM_API_TOKEN_NAME_LENGTH)
    ]
    project_key: str = Field(min_length=1, max_length=10)
    expires_in_days: int = Field(default=DEFAULT_API_TOKEN_LIFETIME_DAYS, ge=1, le=MAXIMUM_API_TOKEN_LIFETIME_DAYS)
    scope: ApiTokenScope = ApiTokenScope.MCP

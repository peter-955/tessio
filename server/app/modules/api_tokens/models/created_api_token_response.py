from app.modules.api_tokens.models.api_token_response import ApiTokenResponse
from app.shared.common import WireModel


class CreatedApiTokenResponse(WireModel):
    token: str
    api_token: ApiTokenResponse

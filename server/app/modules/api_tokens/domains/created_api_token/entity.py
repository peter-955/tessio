from app.modules.api_tokens.domains.api_token_summary.entity import ApiTokenSummary
from app.shared.common import Entity


class CreatedApiToken(Entity):
    token: str
    summary: ApiTokenSummary

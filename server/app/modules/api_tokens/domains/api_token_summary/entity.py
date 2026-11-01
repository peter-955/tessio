from app.modules.api_tokens.domains.api_token.entity import ApiToken
from app.shared.common import Entity


class ApiTokenSummary(Entity):
    api_token: ApiToken
    project_key: str
    project_name: str

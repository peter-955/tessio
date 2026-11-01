from pydantic import SecretStr

from app.shared.common import Entity


class JiraCredentials(Entity):
    site_url: str
    account_email: str
    api_token: SecretStr

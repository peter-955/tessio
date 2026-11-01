from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class JiraConnection(Entity):
    site_url: str
    account_email: str
    api_token_encrypted: bytes
    account_id: str
    account_display_name: str
    configured_by: UUID
    configured_at: datetime

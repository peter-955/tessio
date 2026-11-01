from datetime import datetime

from app.shared.common import WireModel


class JiraConnectionResponse(WireModel):
    is_configured: bool
    site_url: str | None
    account_email: str | None
    account_display_name: str | None
    configured_at: datetime | None

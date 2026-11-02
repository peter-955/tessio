from datetime import datetime

from app.modules.jira.typing.enums import JiraPermission
from app.shared.common import WireModel


class JiraConnectionResponse(WireModel):
    is_configured: bool
    site_url: str | None
    account_email: str | None
    account_display_name: str | None
    configured_at: datetime | None
    can_create_issues: bool | None
    can_comment: bool | None
    missing_permissions: list[JiraPermission]
    permissions_checked_at: datetime | None

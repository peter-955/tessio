from datetime import datetime

from app.modules.jira.typing.enums import JiraPermission
from app.shared.common import WireModel


class ProjectJiraWriteAccessResponse(WireModel):
    is_project_linked: bool
    is_connection_configured: bool
    can_create_issues: bool | None
    can_comment: bool | None
    missing_permissions: list[JiraPermission]
    checked_at: datetime | None

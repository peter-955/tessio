from collections.abc import Collection
from datetime import datetime

from app.modules.jira.domains.jira_write_access.entity import JiraWriteAccess
from app.modules.jira.typing.constants import JIRA_WRITE_PERMISSIONS
from app.modules.jira.typing.enums import JiraPermission


def build_jira_write_access(missing_permissions: Collection[JiraPermission], checked_at: datetime) -> JiraWriteAccess:
    return JiraWriteAccess(
        can_create_issues=JiraPermission.CREATE_ISSUES not in missing_permissions,
        can_comment=JiraPermission.ADD_COMMENTS not in missing_permissions,
        missing_permissions=[permission for permission in JIRA_WRITE_PERMISSIONS if permission in missing_permissions],
        checked_at=checked_at,
    )

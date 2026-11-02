from datetime import datetime

from app.modules.jira.typing.enums import JiraPermission
from app.shared.common import Entity


class JiraWriteAccess(Entity):
    can_create_issues: bool | None
    can_comment: bool | None
    missing_permissions: list[JiraPermission]
    checked_at: datetime | None

    @property
    def is_create_refused(self) -> bool:
        return self.can_create_issues is False

    @property
    def is_comment_refused(self) -> bool:
        return self.can_comment is False

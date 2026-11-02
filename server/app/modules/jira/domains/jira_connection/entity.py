from datetime import datetime
from uuid import UUID

from pydantic import Field

from app.modules.jira.domains.jira_write_access.entity import JiraWriteAccess
from app.modules.jira.typing.enums import JiraPermission
from app.shared.common import Entity


class JiraConnection(Entity):
    site_url: str
    account_email: str
    api_token_encrypted: bytes
    account_id: str
    account_display_name: str
    configured_by: UUID
    configured_at: datetime
    can_create_issues: bool | None = None
    can_comment: bool | None = None
    missing_permissions: list[JiraPermission] = Field(default_factory=list)
    permissions_checked_at: datetime | None = None

    @property
    def write_access(self) -> JiraWriteAccess:
        return JiraWriteAccess(
            can_create_issues=self.can_create_issues,
            can_comment=self.can_comment,
            missing_permissions=self.missing_permissions,
            checked_at=self.permissions_checked_at,
        )

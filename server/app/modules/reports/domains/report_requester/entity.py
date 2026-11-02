from uuid import UUID

from app.modules.users import UserLanguage, WorkspaceRole
from app.shared.common import Entity


class ReportRequester(Entity):
    user_id: UUID
    workspace_role: WorkspaceRole
    language: UserLanguage
    is_active: bool

from datetime import datetime
from uuid import UUID

from app.modules.users import UserStatus, WorkspaceRole
from app.shared.common import WireModel


class WorkspaceUserResponse(WireModel):
    id: UUID
    email: str
    name: str
    workspace_role: WorkspaceRole
    status: UserStatus
    is_two_factor_set_up: bool
    avatar_url: str | None
    created_at: datetime
    deactivated_at: datetime | None

from datetime import datetime
from uuid import UUID

from app.modules.users import UserStatus
from app.shared.common import WireModel
from app.shared.permissions import ProjectRole


class ProjectMemberResponse(WireModel):
    user_id: UUID
    name: str
    email: str
    user_status: UserStatus
    role: ProjectRole
    added_at: datetime

from datetime import datetime
from uuid import UUID

from app.modules.users import UserStatus
from app.shared.common import Entity
from app.shared.permissions import ProjectRole


class MemberProfile(Entity):
    user_id: UUID
    name: str
    email: str
    user_status: UserStatus
    role: ProjectRole
    created_at: datetime

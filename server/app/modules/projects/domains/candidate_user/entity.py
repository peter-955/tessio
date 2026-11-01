from uuid import UUID

from app.modules.users import UserStatus
from app.shared.common import Entity


class CandidateUser(Entity):
    user_id: UUID
    name: str
    email: str
    user_status: UserStatus

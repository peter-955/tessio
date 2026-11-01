from uuid import UUID

from app.modules.users import UserStatus
from app.shared.common import WireModel


class MemberCandidateResponse(WireModel):
    user_id: UUID
    name: str
    email: str
    user_status: UserStatus

from uuid import UUID

from app.shared.common import WireModel
from app.shared.permissions import ProjectRole


class UserProjectAccessResponse(WireModel):
    project_id: UUID
    project_key: str
    project_name: str
    role: ProjectRole
    is_archived: bool

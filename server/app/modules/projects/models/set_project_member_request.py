from app.shared.common import WireModel
from app.shared.permissions import ProjectRole


class SetProjectMemberRequest(WireModel):
    role: ProjectRole

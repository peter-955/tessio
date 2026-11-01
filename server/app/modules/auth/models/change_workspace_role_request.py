from app.modules.auth.typing.types.assignable_workspace_role import AssignableWorkspaceRole
from app.shared.common import WireModel


class ChangeWorkspaceRoleRequest(WireModel):
    workspace_role: AssignableWorkspaceRole

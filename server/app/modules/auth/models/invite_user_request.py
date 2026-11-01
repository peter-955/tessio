from pydantic import Field

from app.modules.auth.typing.constants.user_management import EMAIL_PATTERN
from app.modules.auth.typing.types.assignable_workspace_role import AssignableWorkspaceRole
from app.modules.auth.typing.types.user_name import UserName
from app.modules.users import WorkspaceRole
from app.shared.common import WireModel


class InviteUserRequest(WireModel):
    email: str = Field(max_length=320, pattern=EMAIL_PATTERN)
    name: UserName
    workspace_role: AssignableWorkspaceRole = WorkspaceRole.MEMBER

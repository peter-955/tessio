from typing import Literal

from app.modules.users import WorkspaceRole

AssignableWorkspaceRole = Literal[WorkspaceRole.ADMIN, WorkspaceRole.MEMBER]

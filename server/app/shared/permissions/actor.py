from uuid import UUID

from app.shared.common import Entity
from app.shared.permissions.workspace_role import WorkspaceRole


class Actor(Entity):
    user_id: UUID
    workspace_role: WorkspaceRole
    api_token_id: UUID | None = None
    token_project_id: UUID | None = None

    @property
    def is_workspace_admin(self) -> bool:
        return self.workspace_role in {WorkspaceRole.OWNER, WorkspaceRole.ADMIN}

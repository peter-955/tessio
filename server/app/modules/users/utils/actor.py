from app.modules.users.domains.user.entity import User
from app.shared.permissions import Actor, WorkspaceRole


def build_actor(user: User) -> Actor:
    return Actor(user_id=user.id, workspace_role=WorkspaceRole(user.workspace_role.value))

from app.modules.auth.errors import CannotChangeOwnOrOwnerError, OwnerOnlyError
from app.modules.users import User, WorkspaceRole
from app.shared.permissions import Actor


def ensure_can_manage_user(actor: Actor, target: User) -> None:
    if target.id == actor.user_id or target.workspace_role is WorkspaceRole.OWNER:
        raise CannotChangeOwnOrOwnerError
    if target.workspace_role is WorkspaceRole.ADMIN and actor.workspace_role.value != WorkspaceRole.OWNER.value:
        raise OwnerOnlyError

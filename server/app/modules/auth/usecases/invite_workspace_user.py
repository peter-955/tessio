from app.modules.auth.errors import OwnerOnlyError
from app.modules.auth.usecases.invite_user import InviteUserUseCase
from app.modules.users import User, WorkspaceRole
from app.shared.permissions import Actor, WorkspaceCapability, require_workspace


class InviteWorkspaceUserUseCase:
    def __init__(self, invite_user: InviteUserUseCase) -> None:
        self._invite_user = invite_user

    async def execute(self, actor: Actor, email: str, name: str, workspace_role: WorkspaceRole) -> User:
        require_workspace(actor, WorkspaceCapability.USER_MANAGE)
        if workspace_role is WorkspaceRole.OWNER:
            raise OwnerOnlyError
        if workspace_role is WorkspaceRole.ADMIN and actor.workspace_role.value != WorkspaceRole.OWNER.value:
            raise OwnerOnlyError
        return await self._invite_user.execute(email, name, workspace_role)

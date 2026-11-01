from app.modules.auth.models.workspace_user_response import WorkspaceUserResponse
from app.modules.auth.utils.avatar_url import build_avatar_url
from app.modules.users import User


def build_workspace_user_response(user: User) -> WorkspaceUserResponse:
    return WorkspaceUserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        workspace_role=user.workspace_role,
        status=user.status,
        is_two_factor_set_up=user.is_two_factor_set_up,
        avatar_url=build_avatar_url(user),
        created_at=user.created_at,
        deactivated_at=user.deactivated_at,
    )

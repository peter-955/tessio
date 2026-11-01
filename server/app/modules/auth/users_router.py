from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, status
from fastapi.responses import RedirectResponse

from app.modules.auth.dependencies import (
    get_change_workspace_role,
    get_deactivate_user,
    get_get_avatar_link,
    get_get_workspace_user,
    get_invite_workspace_user,
    get_list_workspace_users,
    get_reactivate_user,
    get_resend_invite,
    get_reset_user_two_factor,
    get_signed_in_session,
    get_workspace_actor,
)
from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.models.change_workspace_role_request import ChangeWorkspaceRoleRequest
from app.modules.auth.models.invite_user_request import InviteUserRequest
from app.modules.auth.models.workspace_user_response import WorkspaceUserResponse
from app.modules.auth.typing.constants.user_management import AVATAR_CACHE_CONTROL, MAX_USER_QUERY_LENGTH
from app.modules.auth.usecases.change_workspace_role import ChangeWorkspaceRoleUseCase
from app.modules.auth.usecases.deactivate_user import DeactivateUserUseCase
from app.modules.auth.usecases.get_avatar_link import GetAvatarLinkUseCase
from app.modules.auth.usecases.get_workspace_user import GetWorkspaceUserUseCase
from app.modules.auth.usecases.invite_workspace_user import InviteWorkspaceUserUseCase
from app.modules.auth.usecases.list_workspace_users import ListWorkspaceUsersUseCase
from app.modules.auth.usecases.reactivate_user import ReactivateUserUseCase
from app.modules.auth.usecases.resend_invite import ResendInviteUseCase
from app.modules.auth.usecases.reset_user_two_factor import ResetUserTwoFactorUseCase
from app.modules.auth.utils.workspace_user_response import build_workspace_user_response
from app.modules.users import UserStatus, WorkspaceRole
from app.shared.permissions import Actor

users_router = APIRouter(prefix="/api/users", tags=["users"])

WorkspaceActor = Annotated[Actor, Depends(get_workspace_actor)]
SignedInSession = Annotated[AuthenticatedSession, Depends(get_signed_in_session)]


@users_router.get("")
async def list_workspace_users(
    actor: WorkspaceActor,
    use_case: Annotated[ListWorkspaceUsersUseCase, Depends(get_list_workspace_users)],
    user_status: Annotated[UserStatus | None, Query(alias="status")] = None,
    workspace_role: Annotated[WorkspaceRole | None, Query(alias="workspaceRole")] = None,
    query: Annotated[str | None, Query(max_length=MAX_USER_QUERY_LENGTH)] = None,
) -> list[WorkspaceUserResponse]:
    users = await use_case.execute(actor, user_status, workspace_role, query)
    return [build_workspace_user_response(user) for user in users]


@users_router.post("", status_code=status.HTTP_201_CREATED)
async def invite_workspace_user(
    body: InviteUserRequest,
    actor: WorkspaceActor,
    use_case: Annotated[InviteWorkspaceUserUseCase, Depends(get_invite_workspace_user)],
) -> WorkspaceUserResponse:
    return build_workspace_user_response(await use_case.execute(actor, body.email, body.name, body.workspace_role))


@users_router.get("/{user_id}")
async def get_workspace_user(
    user_id: UUID,
    actor: WorkspaceActor,
    use_case: Annotated[GetWorkspaceUserUseCase, Depends(get_get_workspace_user)],
) -> WorkspaceUserResponse:
    return build_workspace_user_response(await use_case.execute(actor, user_id))


@users_router.post("/{user_id}/resend-invite", status_code=status.HTTP_204_NO_CONTENT)
async def resend_invite(
    user_id: UUID,
    actor: WorkspaceActor,
    use_case: Annotated[ResendInviteUseCase, Depends(get_resend_invite)],
) -> None:
    await use_case.execute(actor, user_id)


@users_router.post("/{user_id}/deactivate")
async def deactivate_user(
    user_id: UUID,
    actor: WorkspaceActor,
    use_case: Annotated[DeactivateUserUseCase, Depends(get_deactivate_user)],
) -> WorkspaceUserResponse:
    return build_workspace_user_response(await use_case.execute(actor, user_id))


@users_router.post("/{user_id}/reactivate")
async def reactivate_user(
    user_id: UUID,
    actor: WorkspaceActor,
    use_case: Annotated[ReactivateUserUseCase, Depends(get_reactivate_user)],
) -> WorkspaceUserResponse:
    return build_workspace_user_response(await use_case.execute(actor, user_id))


@users_router.post("/{user_id}/reset-two-factor")
async def reset_user_two_factor(
    user_id: UUID,
    actor: WorkspaceActor,
    use_case: Annotated[ResetUserTwoFactorUseCase, Depends(get_reset_user_two_factor)],
) -> WorkspaceUserResponse:
    return build_workspace_user_response(await use_case.execute(actor, user_id))


@users_router.put("/{user_id}/workspace-role")
async def change_workspace_role(
    user_id: UUID,
    body: ChangeWorkspaceRoleRequest,
    actor: WorkspaceActor,
    use_case: Annotated[ChangeWorkspaceRoleUseCase, Depends(get_change_workspace_role)],
) -> WorkspaceUserResponse:
    return build_workspace_user_response(await use_case.execute(actor, user_id, body.workspace_role))


@users_router.get("/{user_id}/avatar", response_class=RedirectResponse, status_code=status.HTTP_302_FOUND)
async def get_avatar(
    user_id: UUID,
    _: SignedInSession,
    use_case: Annotated[GetAvatarLinkUseCase, Depends(get_get_avatar_link)],
) -> RedirectResponse:
    url = await use_case.execute(user_id)
    return RedirectResponse(url, status_code=status.HTTP_302_FOUND, headers={"Cache-Control": AVATAR_CACHE_CONTROL})

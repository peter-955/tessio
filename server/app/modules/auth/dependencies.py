from collections.abc import Awaitable, Callable
from typing import Annotated

from fastapi import Depends, Request

from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.domains.session_client.entity import SessionClient
from app.modules.auth.errors import NotSignedInError
from app.modules.auth.ports.bearer_token_scope_gate import BearerTokenScopeGate
from app.modules.auth.typing.constants.rate_limit import UNKNOWN_CLIENT_HOST
from app.modules.auth.typing.constants.session_cookie import SESSION_COOKIE_NAME
from app.modules.auth.usecases.accept_invite import AcceptInviteUseCase
from app.modules.auth.usecases.authenticate_session import AuthenticateSessionUseCase
from app.modules.auth.usecases.change_password import ChangePasswordUseCase
from app.modules.auth.usecases.change_workspace_role import ChangeWorkspaceRoleUseCase
from app.modules.auth.usecases.confirm_two_factor_setup import ConfirmTwoFactorSetupUseCase
from app.modules.auth.usecases.deactivate_user import DeactivateUserUseCase
from app.modules.auth.usecases.get_avatar_link import GetAvatarLinkUseCase
from app.modules.auth.usecases.get_workspace_user import GetWorkspaceUserUseCase
from app.modules.auth.usecases.invite_workspace_user import InviteWorkspaceUserUseCase
from app.modules.auth.usecases.list_workspace_users import ListWorkspaceUsersUseCase
from app.modules.auth.usecases.reactivate_user import ReactivateUserUseCase
from app.modules.auth.usecases.regenerate_recovery_codes import RegenerateRecoveryCodesUseCase
from app.modules.auth.usecases.request_password_reset import RequestPasswordResetUseCase
from app.modules.auth.usecases.resend_invite import ResendInviteUseCase
from app.modules.auth.usecases.reset_own_two_factor import ResetOwnTwoFactorUseCase
from app.modules.auth.usecases.reset_password import ResetPasswordUseCase
from app.modules.auth.usecases.reset_user_two_factor import ResetUserTwoFactorUseCase
from app.modules.auth.usecases.sign_in_with_password import SignInWithPasswordUseCase
from app.modules.auth.usecases.sign_out import SignOutUseCase
from app.modules.auth.usecases.sign_out_all import SignOutAllUseCase
from app.modules.auth.usecases.start_two_factor_setup import StartTwoFactorSetupUseCase
from app.modules.auth.usecases.update_profile import UpdateProfileUseCase
from app.modules.auth.usecases.verify_two_factor import VerifyTwoFactorUseCase
from app.modules.users import build_actor
from app.shared.permissions import Actor
from app.shared.rate_limit import RateLimitedError, RateLimiter, RateLimitRule


def get_accept_invite(request: Request) -> AcceptInviteUseCase:
    use_case: AcceptInviteUseCase = request.app.state.container.accept_invite
    return use_case


def get_sign_in_with_password(request: Request) -> SignInWithPasswordUseCase:
    use_case: SignInWithPasswordUseCase = request.app.state.container.sign_in_with_password
    return use_case


def get_start_two_factor_setup(request: Request) -> StartTwoFactorSetupUseCase:
    use_case: StartTwoFactorSetupUseCase = request.app.state.container.start_two_factor_setup
    return use_case


def get_confirm_two_factor_setup(request: Request) -> ConfirmTwoFactorSetupUseCase:
    use_case: ConfirmTwoFactorSetupUseCase = request.app.state.container.confirm_two_factor_setup
    return use_case


def get_verify_two_factor(request: Request) -> VerifyTwoFactorUseCase:
    use_case: VerifyTwoFactorUseCase = request.app.state.container.verify_two_factor
    return use_case


def get_authenticate_session(request: Request) -> AuthenticateSessionUseCase:
    use_case: AuthenticateSessionUseCase = request.app.state.container.authenticate_session
    return use_case


def get_sign_out(request: Request) -> SignOutUseCase:
    use_case: SignOutUseCase = request.app.state.container.sign_out
    return use_case


def get_request_password_reset(request: Request) -> RequestPasswordResetUseCase:
    use_case: RequestPasswordResetUseCase = request.app.state.container.request_password_reset
    return use_case


def get_reset_password(request: Request) -> ResetPasswordUseCase:
    use_case: ResetPasswordUseCase = request.app.state.container.reset_password
    return use_case


def get_list_workspace_users(request: Request) -> ListWorkspaceUsersUseCase:
    use_case: ListWorkspaceUsersUseCase = request.app.state.container.list_workspace_users
    return use_case


def get_get_workspace_user(request: Request) -> GetWorkspaceUserUseCase:
    use_case: GetWorkspaceUserUseCase = request.app.state.container.get_workspace_user
    return use_case


def get_invite_workspace_user(request: Request) -> InviteWorkspaceUserUseCase:
    use_case: InviteWorkspaceUserUseCase = request.app.state.container.invite_workspace_user
    return use_case


def get_resend_invite(request: Request) -> ResendInviteUseCase:
    use_case: ResendInviteUseCase = request.app.state.container.resend_invite
    return use_case


def get_deactivate_user(request: Request) -> DeactivateUserUseCase:
    use_case: DeactivateUserUseCase = request.app.state.container.deactivate_user
    return use_case


def get_reactivate_user(request: Request) -> ReactivateUserUseCase:
    use_case: ReactivateUserUseCase = request.app.state.container.reactivate_user
    return use_case


def get_reset_user_two_factor(request: Request) -> ResetUserTwoFactorUseCase:
    use_case: ResetUserTwoFactorUseCase = request.app.state.container.reset_user_two_factor
    return use_case


def get_change_workspace_role(request: Request) -> ChangeWorkspaceRoleUseCase:
    use_case: ChangeWorkspaceRoleUseCase = request.app.state.container.change_workspace_role
    return use_case


def get_get_avatar_link(request: Request) -> GetAvatarLinkUseCase:
    use_case: GetAvatarLinkUseCase = request.app.state.container.get_avatar_link
    return use_case


def get_update_profile(request: Request) -> UpdateProfileUseCase:
    use_case: UpdateProfileUseCase = request.app.state.container.update_profile
    return use_case


def get_change_password(request: Request) -> ChangePasswordUseCase:
    use_case: ChangePasswordUseCase = request.app.state.container.change_password
    return use_case


def get_regenerate_recovery_codes(request: Request) -> RegenerateRecoveryCodesUseCase:
    use_case: RegenerateRecoveryCodesUseCase = request.app.state.container.regenerate_recovery_codes
    return use_case


def get_reset_own_two_factor(request: Request) -> ResetOwnTwoFactorUseCase:
    use_case: ResetOwnTwoFactorUseCase = request.app.state.container.reset_own_two_factor
    return use_case


def get_sign_out_all(request: Request) -> SignOutAllUseCase:
    use_case: SignOutAllUseCase = request.app.state.container.sign_out_all
    return use_case


def get_is_session_cookie_secure(request: Request) -> bool:
    is_secure: bool = request.app.state.container.is_session_cookie_secure
    return is_secure


def limit_client_requests(rule: RateLimitRule) -> Callable[[Request], Awaitable[None]]:
    async def check_client_rate_limit(request: Request) -> None:
        rate_limiter: RateLimiter = request.app.state.container.rate_limiter
        client_host = UNKNOWN_CLIENT_HOST if request.client is None else request.client.host
        decision = await rate_limiter.hit(client_host, rule)
        if not decision.is_allowed:
            raise RateLimitedError(decision.retry_after_seconds)

    return check_client_rate_limit


def get_session_client(request: Request) -> SessionClient:
    return SessionClient(
        user_agent=request.headers.get("user-agent"),
        ip=None if request.client is None else request.client.host,
    )


def get_bearer_token_scope_gate(request: Request) -> BearerTokenScopeGate:
    gate: BearerTokenScopeGate = request.app.state.container.bearer_token_scope_gate
    return gate


def has_session_cookie(request: Request) -> bool:
    return SESSION_COOKIE_NAME in request.cookies


async def get_authenticated_session(
    request: Request,
    use_case: Annotated[AuthenticateSessionUseCase, Depends(get_authenticate_session)],
) -> AuthenticatedSession:
    token = request.cookies.get(SESSION_COOKIE_NAME)
    if token is None:
        await get_bearer_token_scope_gate(request).refuse_on_session_route(request.headers.get("authorization", ""))
        raise NotSignedInError
    return await use_case.execute(token)


async def get_signed_in_session(
    authenticated: Annotated[AuthenticatedSession, Depends(get_authenticated_session)],
) -> AuthenticatedSession:
    if not authenticated.user_session.is_two_factor_passed:
        raise NotSignedInError
    return authenticated


async def get_workspace_actor(
    authenticated: Annotated[AuthenticatedSession, Depends(get_signed_in_session)],
) -> Actor:
    return build_actor(authenticated.user)


async def authenticate_signed_in_request(request: Request) -> AuthenticatedSession:
    return await get_signed_in_session(await get_authenticated_session(request, get_authenticate_session(request)))

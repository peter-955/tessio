from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.modules.auth.dependencies import (
    get_accept_invite,
    get_authenticated_session,
    get_confirm_two_factor_setup,
    get_is_session_cookie_secure,
    get_request_password_reset,
    get_reset_password,
    get_session_client,
    get_sign_in_with_password,
    get_sign_out,
    get_sign_out_all,
    get_signed_in_session,
    get_start_two_factor_setup,
    get_verify_two_factor,
    limit_client_requests,
)
from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.domains.session_client.entity import SessionClient
from app.modules.auth.models.accept_invite_request import AcceptInviteRequest
from app.modules.auth.models.current_user_response import CurrentUserResponse
from app.modules.auth.models.forgot_password_request import ForgotPasswordRequest
from app.modules.auth.models.recovery_codes_response import RecoveryCodesResponse
from app.modules.auth.models.reset_password_request import ResetPasswordRequest
from app.modules.auth.models.sign_in_request import SignInRequest
from app.modules.auth.models.sign_in_response import SignInResponse
from app.modules.auth.models.two_factor_code_request import TwoFactorCodeRequest
from app.modules.auth.models.two_factor_setup_response import TwoFactorSetupResponse
from app.modules.auth.typing.constants.rate_limit import (
    ONE_TIME_LINK_RATE_LIMIT,
    PASSWORD_FORGOT_RATE_LIMIT,
    SIGN_IN_RATE_LIMIT,
    TWO_FACTOR_RATE_LIMIT,
)
from app.modules.auth.usecases.accept_invite import AcceptInviteUseCase
from app.modules.auth.usecases.confirm_two_factor_setup import ConfirmTwoFactorSetupUseCase
from app.modules.auth.usecases.request_password_reset import RequestPasswordResetUseCase
from app.modules.auth.usecases.reset_password import ResetPasswordUseCase
from app.modules.auth.usecases.sign_in_with_password import SignInWithPasswordUseCase
from app.modules.auth.usecases.sign_out import SignOutUseCase
from app.modules.auth.usecases.sign_out_all import SignOutAllUseCase
from app.modules.auth.usecases.start_two_factor_setup import StartTwoFactorSetupUseCase
from app.modules.auth.usecases.verify_two_factor import VerifyTwoFactorUseCase
from app.modules.auth.utils.current_user_response import build_current_user_response
from app.modules.auth.utils.session_cookie import clear_session_cookie, set_session_cookie
from app.modules.auth.utils.sign_in_step import resolve_sign_in_step

auth_router = APIRouter(prefix="/api/auth", tags=["auth"])

AnySession = Annotated[AuthenticatedSession, Depends(get_authenticated_session)]
SignedInSession = Annotated[AuthenticatedSession, Depends(get_signed_in_session)]
IsCookieSecure = Annotated[bool, Depends(get_is_session_cookie_secure)]
Client = Annotated[SessionClient, Depends(get_session_client)]


@auth_router.post("/invites/{token}", dependencies=[Depends(limit_client_requests(ONE_TIME_LINK_RATE_LIMIT))])
async def accept_invite(
    token: str,
    body: AcceptInviteRequest,
    response: Response,
    client: Client,
    is_cookie_secure: IsCookieSecure,
    use_case: Annotated[AcceptInviteUseCase, Depends(get_accept_invite)],
) -> SignInResponse:
    issued_session = await use_case.execute(token, body.password, client)
    set_session_cookie(response, issued_session.token, is_cookie_secure)
    return SignInResponse(next_step=issued_session.next_step)


@auth_router.post("/sign-in", dependencies=[Depends(limit_client_requests(SIGN_IN_RATE_LIMIT))])
async def sign_in(
    body: SignInRequest,
    response: Response,
    client: Client,
    is_cookie_secure: IsCookieSecure,
    use_case: Annotated[SignInWithPasswordUseCase, Depends(get_sign_in_with_password)],
) -> SignInResponse:
    issued_session = await use_case.execute(body.email, body.password, client)
    set_session_cookie(response, issued_session.token, is_cookie_secure)
    return SignInResponse(next_step=issued_session.next_step)


@auth_router.post("/two-factor/setup")
async def start_two_factor_setup(
    authenticated: AnySession,
    use_case: Annotated[StartTwoFactorSetupUseCase, Depends(get_start_two_factor_setup)],
) -> TwoFactorSetupResponse:
    setup = await use_case.execute(authenticated)
    return TwoFactorSetupResponse(key=setup.key, setup_uri=setup.setup_uri)


@auth_router.post("/two-factor/confirm", dependencies=[Depends(limit_client_requests(TWO_FACTOR_RATE_LIMIT))])
async def confirm_two_factor_setup(
    body: TwoFactorCodeRequest,
    response: Response,
    authenticated: AnySession,
    is_cookie_secure: IsCookieSecure,
    use_case: Annotated[ConfirmTwoFactorSetupUseCase, Depends(get_confirm_two_factor_setup)],
) -> RecoveryCodesResponse:
    confirmed = await use_case.execute(authenticated, body.code)
    set_session_cookie(response, confirmed.issued_session.token, is_cookie_secure)
    return RecoveryCodesResponse(next_step=confirmed.issued_session.next_step, recovery_codes=confirmed.recovery_codes)


@auth_router.post("/two-factor", dependencies=[Depends(limit_client_requests(TWO_FACTOR_RATE_LIMIT))])
async def verify_two_factor(
    body: TwoFactorCodeRequest,
    response: Response,
    authenticated: AnySession,
    is_cookie_secure: IsCookieSecure,
    use_case: Annotated[VerifyTwoFactorUseCase, Depends(get_verify_two_factor)],
) -> SignInResponse:
    issued_session = await use_case.execute(authenticated, body.code)
    set_session_cookie(response, issued_session.token, is_cookie_secure)
    return SignInResponse(next_step=issued_session.next_step)


@auth_router.get("/me")
async def get_current_user(authenticated: AnySession) -> CurrentUserResponse:
    return build_current_user_response(authenticated.user, resolve_sign_in_step(authenticated))


@auth_router.post("/sign-out", status_code=status.HTTP_204_NO_CONTENT)
async def sign_out(
    response: Response,
    authenticated: AnySession,
    is_cookie_secure: IsCookieSecure,
    use_case: Annotated[SignOutUseCase, Depends(get_sign_out)],
) -> None:
    await use_case.execute(authenticated.user_session.id)
    clear_session_cookie(response, is_cookie_secure)


@auth_router.post("/sign-out-all", status_code=status.HTTP_204_NO_CONTENT)
async def sign_out_all(
    response: Response,
    authenticated: SignedInSession,
    is_cookie_secure: IsCookieSecure,
    use_case: Annotated[SignOutAllUseCase, Depends(get_sign_out_all)],
) -> None:
    await use_case.execute(authenticated.user.id)
    clear_session_cookie(response, is_cookie_secure)


@auth_router.post(
    "/password/forgot",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(limit_client_requests(PASSWORD_FORGOT_RATE_LIMIT))],
)
async def request_password_reset(
    body: ForgotPasswordRequest,
    use_case: Annotated[RequestPasswordResetUseCase, Depends(get_request_password_reset)],
) -> None:
    await use_case.execute(body.email)


@auth_router.post(
    "/password/reset",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(limit_client_requests(ONE_TIME_LINK_RATE_LIMIT))],
)
async def reset_password(
    body: ResetPasswordRequest,
    use_case: Annotated[ResetPasswordUseCase, Depends(get_reset_password)],
) -> None:
    await use_case.execute(body.token, body.password)

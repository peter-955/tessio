from typing import Annotated

from fastapi import APIRouter, Depends, Response, status

from app.modules.auth.dependencies import (
    get_change_password,
    get_is_session_cookie_secure,
    get_regenerate_recovery_codes,
    get_reset_own_two_factor,
    get_session_client,
    get_signed_in_session,
    get_update_profile,
)
from app.modules.auth.domains.authenticated_session.entity import AuthenticatedSession
from app.modules.auth.domains.profile_changes.entity import ProfileChanges
from app.modules.auth.domains.session_client.entity import SessionClient
from app.modules.auth.models.change_password_request import ChangePasswordRequest
from app.modules.auth.models.current_user_response import CurrentUserResponse
from app.modules.auth.models.password_confirmation_request import PasswordConfirmationRequest
from app.modules.auth.models.recovery_code_list_response import RecoveryCodeListResponse
from app.modules.auth.models.sign_in_response import SignInResponse
from app.modules.auth.models.update_profile_request import UpdateProfileRequest
from app.modules.auth.typing.enums import SignInStep
from app.modules.auth.usecases.change_password import ChangePasswordUseCase
from app.modules.auth.usecases.regenerate_recovery_codes import RegenerateRecoveryCodesUseCase
from app.modules.auth.usecases.reset_own_two_factor import ResetOwnTwoFactorUseCase
from app.modules.auth.usecases.update_profile import UpdateProfileUseCase
from app.modules.auth.utils.current_user_response import build_current_user_response
from app.modules.auth.utils.session_cookie import set_session_cookie

me_router = APIRouter(prefix="/api/me", tags=["me"])

SignedInSession = Annotated[AuthenticatedSession, Depends(get_signed_in_session)]
IsCookieSecure = Annotated[bool, Depends(get_is_session_cookie_secure)]
Client = Annotated[SessionClient, Depends(get_session_client)]


@me_router.patch("")
async def update_profile(
    body: UpdateProfileRequest,
    authenticated: SignedInSession,
    use_case: Annotated[UpdateProfileUseCase, Depends(get_update_profile)],
) -> CurrentUserResponse:
    changes = ProfileChanges(
        name=body.name,
        language=body.language,
        color_scheme=body.color_scheme,
        avatar_file_id=body.avatar_file_id,
        is_avatar_changed="avatar_file_id" in body.model_fields_set,
    )
    user = await use_case.execute(authenticated, changes)
    return build_current_user_response(user, SignInStep.SIGNED_IN)


@me_router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(
    body: ChangePasswordRequest,
    authenticated: SignedInSession,
    use_case: Annotated[ChangePasswordUseCase, Depends(get_change_password)],
) -> None:
    await use_case.execute(authenticated, body.current_password, body.new_password)


@me_router.post("/recovery-codes")
async def regenerate_recovery_codes(
    body: PasswordConfirmationRequest,
    authenticated: SignedInSession,
    use_case: Annotated[RegenerateRecoveryCodesUseCase, Depends(get_regenerate_recovery_codes)],
) -> RecoveryCodeListResponse:
    return RecoveryCodeListResponse(recovery_codes=await use_case.execute(authenticated, body.password))


@me_router.post("/two-factor/reset")
async def reset_own_two_factor(
    body: PasswordConfirmationRequest,
    response: Response,
    authenticated: SignedInSession,
    client: Client,
    is_cookie_secure: IsCookieSecure,
    use_case: Annotated[ResetOwnTwoFactorUseCase, Depends(get_reset_own_two_factor)],
) -> SignInResponse:
    issued_session = await use_case.execute(authenticated, body.password, client)
    set_session_cookie(response, issued_session.token, is_cookie_secure)
    return SignInResponse(next_step=issued_session.next_step)

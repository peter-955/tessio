from app.modules.auth.models.current_user_response import CurrentUserResponse
from app.modules.auth.typing.enums import SignInStep
from app.modules.auth.utils.avatar_url import build_avatar_url
from app.modules.users import User


def build_current_user_response(user: User, next_step: SignInStep) -> CurrentUserResponse:
    return CurrentUserResponse(
        id=user.id,
        email=user.email,
        name=user.name,
        workspace_role=user.workspace_role,
        next_step=next_step,
        language=user.language,
        color_scheme=user.color_scheme,
        avatar_file_id=user.avatar_file_id,
        avatar_url=build_avatar_url(user),
        is_two_factor_set_up=user.is_two_factor_set_up,
    )

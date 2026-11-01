from uuid import UUID

from app.modules.auth.typing.enums import SignInStep
from app.modules.users import ColorScheme, UserLanguage, WorkspaceRole
from app.shared.common import WireModel


class CurrentUserResponse(WireModel):
    id: UUID
    email: str
    name: str
    workspace_role: WorkspaceRole
    next_step: SignInStep
    language: UserLanguage
    color_scheme: ColorScheme
    avatar_file_id: UUID | None
    avatar_url: str | None
    is_two_factor_set_up: bool

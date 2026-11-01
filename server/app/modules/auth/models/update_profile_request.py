from uuid import UUID

from app.modules.auth.typing.types.user_name import UserName
from app.modules.users import ColorScheme, UserLanguage
from app.shared.common import WireModel


class UpdateProfileRequest(WireModel):
    name: UserName | None = None
    language: UserLanguage | None = None
    color_scheme: ColorScheme | None = None
    avatar_file_id: UUID | None = None

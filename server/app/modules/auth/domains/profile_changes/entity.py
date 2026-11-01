from uuid import UUID

from app.modules.users import ColorScheme, UserLanguage
from app.shared.common import Entity


class ProfileChanges(Entity):
    name: str | None = None
    language: UserLanguage | None = None
    color_scheme: ColorScheme | None = None
    avatar_file_id: UUID | None = None
    is_avatar_changed: bool = False

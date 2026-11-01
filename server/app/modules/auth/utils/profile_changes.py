from app.modules.auth.domains.profile_changes.entity import ProfileChanges
from app.modules.users import User


def apply_profile_changes(user: User, changes: ProfileChanges) -> User:
    return user.model_copy(
        update={
            "name": user.name if changes.name is None else changes.name.strip(),
            "language": user.language if changes.language is None else changes.language,
            "color_scheme": user.color_scheme if changes.color_scheme is None else changes.color_scheme,
            "avatar_file_id": changes.avatar_file_id if changes.is_avatar_changed else user.avatar_file_id,
        }
    )

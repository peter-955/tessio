from app.modules.users import User


def build_avatar_url(user: User) -> str | None:
    if user.avatar_file_id is None:
        return None
    return f"/api/users/{user.id}/avatar?v={user.avatar_file_id}"

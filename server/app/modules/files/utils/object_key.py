from uuid import UUID

from app.modules.files.typing.enums import StoredFileKind


def build_object_key_directory(project_id: UUID, kind: StoredFileKind, file_id: UUID) -> str:
    return f"projects/{project_id}/{kind}/{file_id}/"


def build_object_key(project_id: UUID, kind: StoredFileKind, file_id: UUID, file_name: str) -> str:
    return f"{build_object_key_directory(project_id, kind, file_id)}{file_name}"


def build_avatar_object_key_directory(user_id: UUID, file_id: UUID) -> str:
    return f"users/{user_id}/avatar/{file_id}/"


def build_avatar_object_key(user_id: UUID, file_id: UUID, file_name: str) -> str:
    return f"{build_avatar_object_key_directory(user_id, file_id)}{file_name}"


def build_screenshot_key_prefix(project_id: UUID, case_result_id: UUID) -> str:
    return f"projects/{project_id}/{StoredFileKind.SCREENSHOT}/{case_result_id}/"

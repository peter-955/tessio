from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class ProjectNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Project not found.")


class PermissionDeniedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.PERMISSION_DENIED, "You do not have permission to do this.")


class ProjectArchivedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.PROJECT_ARCHIVED, "This project is archived and read-only.")

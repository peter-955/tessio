from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class ProjectKeyAlreadyUsedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.PROJECT_KEY_ALREADY_USED, "A project with this key already exists.")


class JiraProjectAlreadyLinkedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.JIRA_PROJECT_ALREADY_LINKED, "This Jira project is already linked to a project.")


class JiraNotConfiguredError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.JIRA_NOT_CONFIGURED, "Connect Jira before creating a project.")


class LastProjectAdminError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.LAST_PROJECT_ADMIN, "A project needs at least one Admin.")


class UserDeactivatedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.USER_DEACTIVATED, "This user is deactivated.")


class UserNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "User not found.")


class ProjectMemberNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "This user is not a member of the project.")


class DefaultEnvironmentNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, "Pick an active environment of this project.")

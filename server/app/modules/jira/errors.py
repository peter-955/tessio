from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class JiraNotConfiguredError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.JIRA_NOT_CONFIGURED, "Connect Jira first.")


class JiraInvalidCredentialsError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.JIRA_INVALID_CREDENTIALS, "Jira refused this email and API token.")


class JiraUnreachableError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.JIRA_UNREACHABLE, "Jira could not be reached. Try again later.")


class JiraProjectNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Jira project not found.")


class InvalidJiraSiteUrlError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.INVALID_REQUEST, "Enter your Jira site URL, for example https://your-team.atlassian.net."
        )


class JiraApiTokenRequiredError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Enter the API token.")

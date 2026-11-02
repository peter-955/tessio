from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class StoryNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Story not found.")


class SprintNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Sprint not found.")


class InvalidTestStatusTransitionError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_STATUS_TRANSITION, "This test status change is not allowed.")


class StorySignOffBlockedError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.STORY_SIGN_OFF_BLOCKED,
            "Resolve active failures and wait for running runs before marking the story Passed.",
        )


class ProjectWithoutJiraError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.JIRA_NOT_CONFIGURED, "This project writes its stories in Tessio, so there is nothing to sync."
        )


class StoriesComeFromJiraError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Stories of this project come from Jira. Change them in Jira.")


class StoryInUseError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CONFLICT, "This story has test cases, runs or gaps, so it can't be deleted.")

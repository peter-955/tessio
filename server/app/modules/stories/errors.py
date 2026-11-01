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

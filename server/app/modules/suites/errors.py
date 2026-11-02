from app.modules.suites.typing.constants.suite import MAX_SUITE_CASES
from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class SuiteNameAlreadyUsedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.SUITE_NAME_ALREADY_USED, "Another suite in this project already has this name.")


class UnknownSuiteCasesError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, "Use only test cases of this project.")


class DuplicateSuiteCaseError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "List each test case only once.")


class TooManySuiteCasesError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, f"A suite holds at most {MAX_SUITE_CASES} test cases.")


class SuiteFilterRequiredError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Pick at least one filter: labels, priorities, story or sprint.")


class UnknownFilterStoryError(TessioError):
    def __init__(self, story_key: str) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, f"No story {story_key} in this project.")


class UnknownFilterSprintError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, "This sprint is not in this project.")

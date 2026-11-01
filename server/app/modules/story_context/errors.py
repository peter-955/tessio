from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class RunNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Run not found.")


class RunNotOwnedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.RUN_NOT_OWNED, "Only the person who started this run can use it.")


class RunNotRunningError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.RUN_NOT_RUNNING, "This run is not running.")


class TestFileNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "No test file with this key in this run.")


class TestFileKeyAmbiguousError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Several cases in this run use this file key; pass case_id.")

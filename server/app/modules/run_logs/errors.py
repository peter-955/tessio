from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class RunNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Run not found.")


class RunLogNotOwnedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.RUN_NOT_OWNED, "Only the person who started the run can send its log.")


class RunLogTooEarlyError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CONFLICT, "Send the log after the run has finished.")


class RunLogTooLateError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CONFLICT, "The log can be sent only within 24 hours after the run finished.")


class RunLogManualRunError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Manual runs have no Claude log.")

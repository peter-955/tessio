from app.shared.common import TessioError
from app.shared.typing.enums import ErrorCode


class RunNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Run not found.")


class RunNotOwnedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.RUN_NOT_OWNED, "Only the person who started this run can do this.")


class RunNotRunningError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.RUN_NOT_RUNNING, "This run is already finished.")


class RunAlreadyRunningError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.RUN_ALREADY_RUNNING, "A run is already in progress for this story.")


class RunNotFinishedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.RUN_NOT_FINISHED, "Finish the run before re-running its failed cases.")


class NoReadyCasesError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NO_READY_CASES, "This story has no Ready test cases to run.")


class CaseNotReadyError(TessioError):
    def __init__(self, code: str) -> None:
        super().__init__(ErrorCode.CASE_NOT_READY, f"{code} is not Ready.")


class UnknownCaseError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, "This test case is not part of this story or run.")


class CaseResultExistsError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.CASE_RESULT_EXISTS, "A result is already recorded for this case in this run.")


class CaseResultNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Case result not found.")


class RunCaseNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "This case is not part of the run.")


class NoFailedCasesToRerunError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NO_FAILED_CASES_TO_RERUN, "No failed or blocked case of this run is still Ready.")


class EnvironmentNotFoundError(TessioError):
    def __init__(self, name: str) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, f"No active environment named {name}.")


class EnvironmentRequiredError(TessioError):
    def __init__(self, names: list[str]) -> None:
        message = f"Pick an environment: {', '.join(names)}." if names else "This project has no active environment."
        super().__init__(ErrorCode.INVALID_REQUEST, message)


class InvalidStepOrderError(TessioError):
    def __init__(self, order: int, code: str) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, f"Step {order} is not a step of {code} or is reported twice.")


class InvalidStepReportError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Each step order must be unique and must exist in the case.")


class ParentRunMismatchError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "The parent run belongs to another story.")


class InvalidRequestError(TessioError):
    def __init__(self, message: str) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, message)


class RunNotManualError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.RUN_NOT_MANUAL, "Only manual runs are recorded here.")


class EvidenceFileNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Evidence file not found.")


class EvidenceNotUploadedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UPLOAD_NOT_COMPLETED, "The evidence file has not finished uploading.")

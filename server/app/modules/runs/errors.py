from app.modules.runs.domains.blocking_gap.entity import BlockingGap
from app.modules.runs.typing.constants.run import MAX_LISTED_BLOCKING_GAPS
from app.modules.runs.utils.blocking_gap import describe_blocking_gap
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
        super().__init__(
            ErrorCode.CASE_RESULT_EXISTS, "A result is already recorded for this case and iteration in this run."
        )


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


class RunTargetRequiredError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "Pass either a story or a suite, not both.")


class SuiteNotFoundError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.NOT_FOUND, "Suite not found.")


class SuiteArchivedError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.SUITE_ARCHIVED, "This suite is archived.")


class SuiteAlreadyRunningError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.SUITE_ALREADY_RUNNING, "A run is already in progress for this suite.")


class SuiteEmptyError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.SUITE_EMPTY, "This suite has no Ready test cases to run.")


class UnknownSuiteCaseError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, "This test case is not part of this suite.")


class SuiteParentRunMismatchError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.INVALID_REQUEST, "The parent run belongs to another story or suite.")


class SuiteOpenGapsBlockRunError(TessioError):
    def __init__(self, gaps: list[BlockingGap]) -> None:
        listed = "; ".join(describe_blocking_gap(gap) for gap in gaps[:MAX_LISTED_BLOCKING_GAPS])
        more = len(gaps) - MAX_LISTED_BLOCKING_GAPS
        suffix = f"; and {more} more" if more > 0 else ""
        super().__init__(
            ErrorCode.OPEN_GAPS_BLOCK_RUN,
            f"{len(gaps)} open gaps block this suite run. Answer them first: {listed}{suffix}",
        )
        self.gaps = gaps


class IterationOutOfRangeError(TessioError):
    def __init__(self, iteration: int, iteration_count: int) -> None:
        super().__init__(
            ErrorCode.ITERATION_OUT_OF_RANGE,
            f"Iteration {iteration} does not exist: this case has {iteration_count} "
            f"iteration{'s' if iteration_count != 1 else ''} (0 to {iteration_count - 1}).",
        )


class JunitInvalidError(TessioError):
    def __init__(self, reason: str) -> None:
        super().__init__(ErrorCode.JUNIT_INVALID, f"This file is not valid JUnit XML: {reason}")


class JunitNoMappedTestsError(TessioError):
    def __init__(self) -> None:
        super().__init__(
            ErrorCode.JUNIT_NO_MAPPED_TESTS,
            "No test in this file names a test case of this project. Put TC-<number> in the test name "
            "or in a tessio.case property.",
        )


class JunitFileTooLargeError(TessioError):
    def __init__(self) -> None:
        super().__init__(ErrorCode.FILE_TOO_LARGE, "JUnit files can be at most 10 MB.")


class UnknownImportEnvironmentError(TessioError):
    def __init__(self, reference: str) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, f"No active environment {reference} in this project.")


class UnknownImportSuiteError(TessioError):
    def __init__(self, reference: str) -> None:
        super().__init__(ErrorCode.UNKNOWN_REFERENCE, f"No suite {reference} in this project.")

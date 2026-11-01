from enum import StrEnum


class RunStatus(StrEnum):
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    ABORTED = "aborted"


class RunExecutor(StrEnum):
    CLAUDE = "claude"
    MANUAL = "manual"


class RunAbortReason(StrEnum):
    NO_RESULTS = "no_results"
    INACTIVE = "inactive"

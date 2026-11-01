from enum import StrEnum


class NotificationKind(StrEnum):
    GAP_ASSIGNED = "gap_assigned"
    FAILURE_ASSIGNED = "failure_assigned"
    RUN_FINISHED = "run_finished"


class RunOutcome(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    ABORTED = "aborted"

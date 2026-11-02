from enum import StrEnum


class NotificationKind(StrEnum):
    GAP_ASSIGNED = "gap_assigned"
    FAILURE_ASSIGNED = "failure_assigned"
    RUN_FINISHED = "run_finished"
    SUITE_RUN_FINISHED = "suite_run_finished"
    REPORT_READY = "report_ready"


class RunOutcome(StrEnum):
    PASSED = "passed"
    FAILED = "failed"
    ABORTED = "aborted"


class NotificationChannel(StrEnum):
    IN_APP = "in_app"
    EMAIL = "email"

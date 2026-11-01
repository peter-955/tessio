from enum import StrEnum


class CriterionStatus(StrEnum):
    UNCOVERED = "uncovered"
    NOT_RUN = "not_run"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"

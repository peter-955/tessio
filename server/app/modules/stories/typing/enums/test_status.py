from enum import StrEnum


class TestStatus(StrEnum):
    NOT_STARTED = "not_started"
    READY_FOR_TEST = "ready_for_test"
    IN_TEST = "in_test"
    PASSED = "passed"
    FAILED = "failed"

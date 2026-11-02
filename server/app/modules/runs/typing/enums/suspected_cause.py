from enum import StrEnum


class SuspectedCause(StrEnum):
    APP_BUG = "app_bug"
    TEST_DATA = "test_data"
    ENVIRONMENT = "environment"
    TEST_CASE = "test_case"
    UNKNOWN = "unknown"

from enum import StrEnum


class GapType(StrEnum):
    MISSING_ACCEPTANCE_CRITERIA = "missing_ac"
    UNCLEAR_GOAL = "unclear_goal"
    MISSING_STEP = "missing_step"
    MISSING_TEST_DATA = "missing_test_data"
    OTHER = "other"


class GapTargetType(StrEnum):
    STORY = "story"
    CRITERION = "criterion"
    TEST_CASE = "test_case"


class GapSeverity(StrEnum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class GapStatus(StrEnum):
    OPEN = "open"
    RESOLVED = "resolved"


class GapDataScope(StrEnum):
    PROJECT = "project"
    ENVIRONMENT = "environment"

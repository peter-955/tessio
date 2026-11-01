from enum import StrEnum


class TestCaseStatus(StrEnum):
    DRAFT = "draft"
    IN_REVIEW = "in_review"
    READY = "ready"
    DEPRECATED = "deprecated"


class TestCasePriority(StrEnum):
    CRITICAL = "critical"
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class CaseImportFormat(StrEnum):
    XLSX = "xlsx"
    CSV = "csv"


class CaseImportProblem(StrEnum):
    STORY_KEY_MISSING = "story_key_missing"
    STORY_NOT_FOUND = "story_not_found"
    TOO_MANY_STEPS = "too_many_steps"
    TEXT_TOO_LONG = "text_too_long"


class CaseImportSkipReason(StrEnum):
    STEP_WITHOUT_CASE = "step_without_case"
    SHEET_WITHOUT_HEADER = "sheet_without_header"

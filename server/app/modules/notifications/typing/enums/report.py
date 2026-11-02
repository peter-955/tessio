from enum import StrEnum


class ReportFormat(StrEnum):
    MARKDOWN = "md"
    PDF = "pdf"


class ReportSource(StrEnum):
    RUN = "run"
    PLAN = "plan"
    STORY = "story"

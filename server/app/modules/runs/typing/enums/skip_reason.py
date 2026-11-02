from enum import StrEnum


class SkipReason(StrEnum):
    NEEDS_REVIEW = "needs_review"
    NOT_READY = "not_ready"

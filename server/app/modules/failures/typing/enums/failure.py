from enum import StrEnum


class FailureStatus(StrEnum):
    OPEN = "open"
    FIXED = "fixed"
    VERIFIED = "verified"
    REOPENED = "reopened"


class FailureEventKind(StrEnum):
    OPENED = "opened"
    FAILED_AGAIN = "failed_again"
    STATUS_CHANGED = "status_changed"
    ASSIGNED = "assigned"
    UNASSIGNED = "unassigned"

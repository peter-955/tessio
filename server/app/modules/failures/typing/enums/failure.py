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
    CAUSE_CHANGED = "cause_changed"
    JIRA_ISSUE_CREATED = "jira_issue_created"
    JIRA_ISSUE_FAILED = "jira_issue_failed"

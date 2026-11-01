from enum import StrEnum


class JiraSprintState(StrEnum):
    ACTIVE = "active"
    FUTURE = "future"
    CLOSED = "closed"

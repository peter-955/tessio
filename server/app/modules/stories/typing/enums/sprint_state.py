from enum import StrEnum


class SprintState(StrEnum):
    ACTIVE = "active"
    FUTURE = "future"
    CLOSED = "closed"

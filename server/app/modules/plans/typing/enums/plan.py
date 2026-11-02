from enum import StrEnum


class PlanStatus(StrEnum):
    OPEN = "open"
    SIGNED_OFF = "signed_off"
    CLOSED = "closed"


class PlanItemKind(StrEnum):
    SUITE = "suite"
    STORY = "story"

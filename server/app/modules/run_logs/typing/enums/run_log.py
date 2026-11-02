from enum import StrEnum


class RunLogPhase(StrEnum):
    SETUP = "setup"
    CASE = "case"
    WRAP_UP = "wrap_up"


class RunLogEntryKind(StrEnum):
    NOTE = "note"
    ACTION = "action"

from enum import StrEnum


class ResultExecutorKind(StrEnum):
    MANUAL = "manual"
    AUTOMATED = "automated"


class QuarantineEventKind(StrEnum):
    QUARANTINED = "quarantined"
    RELEASED = "released"
    AUTO_RELEASED = "auto_released"

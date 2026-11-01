from enum import StrEnum


class DependencyStatus(StrEnum):
    OK = "ok"
    FAILED = "failed"


class ReadinessStatus(StrEnum):
    READY = "ready"
    NOT_READY = "not_ready"


class LivenessStatus(StrEnum):
    OK = "ok"

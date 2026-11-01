from enum import StrEnum


class ProjectSyncStatus(StrEnum):
    NEVER = "never"
    QUEUED = "queued"
    RUNNING = "running"
    SUCCEEDED = "succeeded"
    FAILED = "failed"

from enum import StrEnum


class QueueName(StrEnum):
    EMAIL = "email"
    JIRA = "jira"
    MAINTENANCE = "maintenance"


class JobName(StrEnum):
    SEND_EMAIL = "email.send"
    JIRA_SYNC_PROJECT = "jira.sync_project"
    RUNS_ABORT_STALE = "runs.abort_stale"
    FILES_DELETE_ORPHANS = "files.delete_orphans"
    SESSIONS_DELETE_EXPIRED = "sessions.delete_expired"

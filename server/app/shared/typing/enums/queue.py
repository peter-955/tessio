from enum import StrEnum


class QueueName(StrEnum):
    EMAIL = "email"
    JIRA = "jira"
    MAINTENANCE = "maintenance"
    INTEGRATIONS = "integrations"
    REPORTS = "reports"


class JobName(StrEnum):
    SEND_EMAIL = "email.send"
    JIRA_SYNC_PROJECT = "jira.sync_project"
    RUNS_ABORT_STALE = "runs.abort_stale"
    FILES_DELETE_ORPHANS = "files.delete_orphans"
    SESSIONS_DELETE_EXPIRED = "sessions.delete_expired"
    TEST_CASES_RECOMPUTE_FLAKY = "test_cases.recompute_flaky"
    TEST_CASES_SWEEP_FLAKY = "test_cases.sweep_flaky"
    JIRA_CREATE_ISSUE = "jira.create_issue"
    JIRA_POST_COMMENT = "jira.post_comment"
    NOTIFICATION_EMAIL = "notification.email"
    CHAT_DELIVER = "chat.deliver"
    WEBHOOK_DELIVER = "webhook.deliver"
    WEBHOOK_DELETE_OLD_DELIVERIES = "webhook.delete_old_deliveries"
    INSIGHTS_DAILY_SNAPSHOT = "insights.daily_snapshot"
    REPORT_EXPORT = "report.export"

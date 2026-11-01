from enum import StrEnum


class LiveEventType(StrEnum):
    RUN_STARTED = "run.started"
    RUN_CASE_RECORDED = "run.case_recorded"
    RUN_FINISHED = "run.finished"
    JIRA_SYNC_STARTED = "jira.sync_started"
    JIRA_SYNC_FINISHED = "jira.sync_finished"
    JIRA_SYNC_FAILED = "jira.sync_failed"
    NOTIFICATION_CREATED = "notification.created"
    PROJECT_MEMBERS_CHANGED = "project.members_changed"
    GAP_CHANGED = "gap.changed"
    FAILURE_CHANGED = "failure.changed"
    TEST_CASE_CHANGED = "test_case.changed"
    STORY_CHANGED = "story.changed"

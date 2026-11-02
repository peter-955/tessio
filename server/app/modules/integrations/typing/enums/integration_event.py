from enum import StrEnum


class IntegrationEvent(StrEnum):
    RUN_STARTED = "run.started"
    RUN_FINISHED = "run.finished"
    FAILURE_OPENED = "failure.opened"
    FAILURE_STATUS_CHANGED = "failure.status_changed"
    GAP_RAISED = "gap.raised"
    STORY_SIGNED_OFF = "story.signed_off"
    PLAN_SIGNED_OFF = "plan.signed_off"

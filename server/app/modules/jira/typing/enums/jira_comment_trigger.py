from enum import StrEnum


class JiraCommentTrigger(StrEnum):
    SIGN_OFF = "sign_off"
    RUN_FINISHED = "run_finished"

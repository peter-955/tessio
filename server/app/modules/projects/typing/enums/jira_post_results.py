from enum import StrEnum


class JiraPostResults(StrEnum):
    OFF = "off"
    ON_SIGN_OFF = "on_sign_off"
    EVERY_RUN = "every_run"

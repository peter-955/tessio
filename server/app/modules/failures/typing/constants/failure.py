from collections.abc import Mapping
from datetime import timedelta

from app.modules.failures.typing.enums import FailureStatus

ACTIVE_FAILURE_STATUSES = frozenset({FailureStatus.OPEN, FailureStatus.FIXED, FailureStatus.REOPENED})
MANUAL_STATUS_TRANSITIONS: Mapping[FailureStatus, frozenset[FailureStatus]] = {
    FailureStatus.OPEN: frozenset({FailureStatus.FIXED}),
    FailureStatus.REOPENED: frozenset({FailureStatus.FIXED}),
    FailureStatus.FIXED: frozenset({FailureStatus.VERIFIED, FailureStatus.REOPENED}),
    FailureStatus.VERIFIED: frozenset(),
}
TEST_CASE_CODE_PREFIX = "TC-"
MAX_FAILURE_LIST_SIZE = 500
MAX_RESULT_HISTORY_SIZE = 50

MAX_CAUSE_REASON_LENGTH = 500
JIRA_ISSUE_PENDING_TIMEOUT = timedelta(minutes=15)
JIRA_CREATE_ISSUE_JOB_ID_TEMPLATE = "jira-create-issue:{failure_id}"
TESSIO_FAILURE_URL_TEMPLATE = "{client_url}/projects/{project_key}/failures/{failure_id}"
JIRA_BUG_LINK_TEXT = "Open the failure in Tessio"
PARAMETER_PLACEHOLDER_PATTERN = r"\{\{\s*param\.([A-Za-z][A-Za-z0-9_.-]{0,99})\s*\}\}"

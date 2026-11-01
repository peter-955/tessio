from collections.abc import Mapping

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

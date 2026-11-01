from collections.abc import Mapping

from app.modules.stories.typing.enums.test_status import TestStatus
from app.shared.permissions import Capability

TEST_STATUS_TRANSITIONS: Mapping[TestStatus, frozenset[TestStatus]] = {
    TestStatus.NOT_STARTED: frozenset({TestStatus.READY_FOR_TEST}),
    TestStatus.READY_FOR_TEST: frozenset({TestStatus.NOT_STARTED}),
    TestStatus.IN_TEST: frozenset({TestStatus.PASSED, TestStatus.FAILED}),
    TestStatus.PASSED: frozenset({TestStatus.FAILED}),
    TestStatus.FAILED: frozenset({TestStatus.PASSED, TestStatus.READY_FOR_TEST}),
}

CAPABILITY_BY_TARGET_STATUS: Mapping[TestStatus, Capability] = {
    TestStatus.NOT_STARTED: Capability.STORY_MARK_READY_FOR_TEST,
    TestStatus.READY_FOR_TEST: Capability.STORY_MARK_READY_FOR_TEST,
    TestStatus.PASSED: Capability.STORY_SIGN_OFF,
    TestStatus.FAILED: Capability.STORY_SIGN_OFF,
}

STORY_QUERY_MAX_LENGTH = 100

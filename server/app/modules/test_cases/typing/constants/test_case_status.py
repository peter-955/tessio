from collections.abc import Mapping

from app.modules.test_cases.typing.enums.test_case import TestCaseStatus

TEST_CASE_STATUS_TRANSITIONS: Mapping[TestCaseStatus, frozenset[TestCaseStatus]] = {
    TestCaseStatus.DRAFT: frozenset({TestCaseStatus.IN_REVIEW, TestCaseStatus.DEPRECATED}),
    TestCaseStatus.IN_REVIEW: frozenset({TestCaseStatus.DRAFT, TestCaseStatus.READY, TestCaseStatus.DEPRECATED}),
    TestCaseStatus.READY: frozenset({TestCaseStatus.IN_REVIEW, TestCaseStatus.DRAFT, TestCaseStatus.DEPRECATED}),
    TestCaseStatus.DEPRECATED: frozenset({TestCaseStatus.DRAFT}),
}

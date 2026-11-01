from app.modules.test_cases import TestCaseStatus

TEST_CASE_CODE_PREFIX = "TC-"
DRAFT_CASE_STATUSES: tuple[TestCaseStatus, ...] = (TestCaseStatus.DRAFT, TestCaseStatus.IN_REVIEW)

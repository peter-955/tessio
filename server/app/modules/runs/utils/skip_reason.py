from app.modules.runs.domains.suite_run_case.entity import SuiteRunCase
from app.modules.runs.typing.enums import SkipReason
from app.modules.test_cases import TestCaseStatus


def find_skip_reason(suite_case: SuiteRunCase) -> SkipReason | None:
    if suite_case.status is not TestCaseStatus.READY:
        return SkipReason.NOT_READY
    if suite_case.is_needing_review:
        return SkipReason.NEEDS_REVIEW
    return None

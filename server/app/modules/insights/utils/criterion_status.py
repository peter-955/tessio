from collections.abc import Sequence

from app.modules.insights.domains.traced_case.entity import TracedCase
from app.modules.runs import CriterionStatus, ResultStatus
from app.modules.test_cases import TestCaseStatus


def resolve_criterion_status(linked: Sequence[TracedCase]) -> CriterionStatus:
    active_cases = [case for case in linked if case.status is not TestCaseStatus.DEPRECATED]
    if not active_cases:
        return CriterionStatus.UNCOVERED
    considered = [
        case for case in active_cases if case.status is TestCaseStatus.READY or case.latest_result is not None
    ]
    if not considered:
        return CriterionStatus.NOT_RUN
    statuses = [None if case.latest_result is None else case.latest_result.status for case in considered]
    if ResultStatus.FAILED in statuses:
        return CriterionStatus.FAILED
    if ResultStatus.BLOCKED in statuses:
        return CriterionStatus.BLOCKED
    if None in statuses or ResultStatus.SKIPPED in statuses:
        return CriterionStatus.NOT_RUN
    return CriterionStatus.PASSED

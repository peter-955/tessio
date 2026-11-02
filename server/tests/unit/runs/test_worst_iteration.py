from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.runs import CaseResult, ResultStatus
from app.modules.runs.utils.worst_iteration import is_new_case_outcome, select_worst_results


def build_result(test_case_id: UUID, status: ResultStatus, iteration: int) -> CaseResult:
    return CaseResult(
        id=uuid7(),
        run_id=uuid7(),
        test_case_id=test_case_id,
        test_case_version_id=uuid7(),
        status=status,
        duration_ms=None,
        suspected_cause=None,
        cause_reason=None,
        recorded_by=uuid7(),
        created_at=datetime.now(UTC),
        iteration=iteration,
    )


def test_the_worst_iteration_is_failed_then_blocked_then_passed_then_skipped() -> None:
    case_id = uuid7()
    other_case_id = uuid7()
    results = [
        build_result(case_id, ResultStatus.PASSED, 0),
        build_result(case_id, ResultStatus.BLOCKED, 1),
        build_result(case_id, ResultStatus.FAILED, 2),
        build_result(case_id, ResultStatus.FAILED, 3),
        build_result(other_case_id, ResultStatus.SKIPPED, 0),
        build_result(other_case_id, ResultStatus.PASSED, 1),
    ]

    worst = select_worst_results(results)

    assert (worst[case_id].status, worst[case_id].iteration) == (ResultStatus.FAILED, 2)
    assert (worst[other_case_id].status, worst[other_case_id].iteration) == (ResultStatus.PASSED, 1)


def test_only_a_worse_iteration_is_a_new_case_outcome() -> None:
    case_id = uuid7()
    passed = build_result(case_id, ResultStatus.PASSED, 0)
    failed = build_result(case_id, ResultStatus.FAILED, 1)
    failed_again = build_result(case_id, ResultStatus.FAILED, 2)

    assert is_new_case_outcome(passed, []) is True
    assert is_new_case_outcome(failed, [passed]) is True
    assert is_new_case_outcome(failed_again, [passed, failed]) is False
    assert is_new_case_outcome(passed, [failed]) is False

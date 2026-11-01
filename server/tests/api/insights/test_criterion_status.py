from datetime import UTC, datetime
from uuid import uuid7

import pytest

from app.modules.insights.domains.latest_result.entity import LatestResult
from app.modules.insights.domains.traced_case.entity import TracedCase
from app.modules.insights.domains.traced_criterion.entity import TracedCriterion
from app.modules.insights.utils.coverage import build_criterion_traces, count_coverage
from app.modules.insights.utils.criterion_status import resolve_criterion_status
from app.modules.runs import CriterionStatus, ResultStatus
from app.modules.test_cases import TestCasePriority as CasePriority
from app.modules.test_cases import TestCaseStatus as CaseStatus

CaseSpec = tuple[CaseStatus, ResultStatus | None]
READY = CaseStatus.READY
DRAFT = CaseStatus.DRAFT
IN_REVIEW = CaseStatus.IN_REVIEW
DEPRECATED = CaseStatus.DEPRECATED


def build_case(status: CaseStatus, result_status: ResultStatus | None, number: int = 1) -> TracedCase:
    latest_result = (
        None
        if result_status is None
        else LatestResult(
            case_result_id=uuid7(),
            run_id=uuid7(),
            status=result_status,
            recorded_at=datetime.now(UTC),
            test_case_version_id=uuid7(),
        )
    )
    return TracedCase(
        id=uuid7(),
        story_id=uuid7(),
        number=number,
        code=f"TC-{number}",
        title=f"Case {number}",
        status=status,
        priority=CasePriority.MEDIUM,
        is_needing_review=False,
        created_by=uuid7(),
        criterion_ids=frozenset(),
        latest_result=latest_result,
    )


@pytest.mark.parametrize(
    ("specs", "expected"),
    [
        ([], CriterionStatus.UNCOVERED),
        ([(DEPRECATED, ResultStatus.FAILED)], CriterionStatus.UNCOVERED),
        ([(DRAFT, None)], CriterionStatus.NOT_RUN),
        ([(IN_REVIEW, None), (DRAFT, None)], CriterionStatus.NOT_RUN),
        ([(READY, None)], CriterionStatus.NOT_RUN),
        ([(READY, ResultStatus.SKIPPED)], CriterionStatus.NOT_RUN),
        ([(READY, ResultStatus.PASSED)], CriterionStatus.PASSED),
        ([(READY, ResultStatus.PASSED), (DRAFT, None)], CriterionStatus.PASSED),
        ([(DRAFT, ResultStatus.PASSED)], CriterionStatus.PASSED),
        ([(READY, ResultStatus.PASSED), (READY, None)], CriterionStatus.NOT_RUN),
        ([(READY, ResultStatus.PASSED), (READY, ResultStatus.SKIPPED)], CriterionStatus.NOT_RUN),
        ([(READY, ResultStatus.BLOCKED), (READY, None)], CriterionStatus.BLOCKED),
        ([(READY, ResultStatus.FAILED), (READY, ResultStatus.BLOCKED)], CriterionStatus.FAILED),
        ([(READY, ResultStatus.FAILED), (READY, None), (READY, ResultStatus.PASSED)], CriterionStatus.FAILED),
        ([(READY, ResultStatus.PASSED), (DEPRECATED, ResultStatus.FAILED)], CriterionStatus.PASSED),
    ],
)
def test_criterion_status_follows_the_precedence_rule(specs: list[CaseSpec], expected: CriterionStatus) -> None:
    linked = [build_case(status, result_status, number) for number, (status, result_status) in enumerate(specs, 1)]

    assert resolve_criterion_status(linked) is expected


def test_traces_order_active_then_removed_and_count_only_active_criteria() -> None:
    story_id = uuid7()
    removed = TracedCriterion(
        id=uuid7(), story_id=story_id, code="AC1", position=1, text="One", removed_at=datetime.now(UTC)
    )
    second = TracedCriterion(id=uuid7(), story_id=story_id, code="AC2", position=2, text="Two", removed_at=None)
    third = TracedCriterion(id=uuid7(), story_id=story_id, code="AC3", position=3, text="Three", removed_at=None)
    late_case = build_case(READY, ResultStatus.PASSED, 9).model_copy(
        update={"criterion_ids": frozenset({second.id, removed.id})}
    )
    early_case = build_case(READY, ResultStatus.PASSED, 2).model_copy(update={"criterion_ids": frozenset({second.id})})
    deprecated_case = build_case(DEPRECATED, ResultStatus.FAILED, 1).model_copy(
        update={"criterion_ids": frozenset({third.id})}
    )

    traces = build_criterion_traces([third, removed, second], [late_case, deprecated_case, early_case])
    coverage = count_coverage(traces)

    assert [trace.criterion.code for trace in traces] == ["AC2", "AC3", "AC1"]
    assert traces[0].linked_case_ids == [early_case.id, late_case.id]
    assert [trace.status for trace in traces] == [
        CriterionStatus.PASSED,
        CriterionStatus.UNCOVERED,
        CriterionStatus.PASSED,
    ]
    assert coverage.model_dump() == {
        "criterion_count": 2,
        "covered_count": 1,
        "passed_count": 1,
        "failed_count": 0,
        "blocked_count": 0,
        "not_run_count": 0,
        "uncovered_count": 1,
    }

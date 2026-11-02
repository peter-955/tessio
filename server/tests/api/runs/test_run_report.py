from datetime import UTC, datetime
from uuid import UUID, uuid4

import pytest

from app.modules.runs import (
    CaseResult,
    ResultStatus,
    RunAbortReason,
    RunStatus,
    StepResult,
    build_run_report,
    resolve_finished_status,
)
from app.modules.runs.domains.missing_screenshot.entity import MissingScreenshot
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.test_cases import TestCasePriority as CasePriority
from app.modules.test_cases import TestCaseVersion as CaseVersion
from app.modules.test_cases import TestStep as CaseStep

NOW = datetime(2026, 11, 1, 9, 30, tzinfo=UTC)
RUN_ID = uuid4()
USER_ID = uuid4()


def build_view(position: int, step_count: int = 3) -> RunCaseView:
    test_case_id = uuid4()
    return RunCaseView(
        test_case_id=test_case_id,
        code=f"TC-{position}",
        position=position,
        version=CaseVersion(
            id=uuid4(),
            test_case_id=test_case_id,
            number=1,
            title=f"Case {position}",
            priority=CasePriority.MEDIUM,
            business_value=None,
            preconditions=None,
            steps=[
                CaseStep(order=order, action=f"Action {order}", expected=None) for order in range(1, step_count + 1)
            ],
            criterion_ids=[],
            data_keys=[],
            file_version_ids=[],
            created_by=USER_ID,
            created_at=NOW,
        ),
    )


def build_result(view: RunCaseView, status: ResultStatus) -> CaseResult:
    return CaseResult(
        id=uuid4(),
        run_id=RUN_ID,
        test_case_id=view.test_case_id,
        test_case_version_id=view.version.id,
        status=status,
        duration_ms=100,
        suspected_cause=None,
        cause_reason=None,
        recorded_by=USER_ID,
        created_at=NOW,
    )


def build_step(case_result_id: UUID, order: int, status: ResultStatus, error: str | None = None) -> StepResult:
    return StepResult(
        id=uuid4(),
        case_result_id=case_result_id,
        step_order=order,
        status=status,
        actual_result=f"Saw {order}",
        error=error,
        screenshot_file_id=None,
        evidence_file_id=None,
        diagnosis=None,
        created_at=NOW,
    )


def test_report_counts_every_status_and_the_unreported_cases() -> None:
    views = [build_view(position) for position in range(1, 7)]
    statuses = [
        ResultStatus.PASSED,
        ResultStatus.FAILED,
        ResultStatus.BLOCKED,
        ResultStatus.SKIPPED,
        ResultStatus.PASSED,
    ]
    results = [build_result(view, status) for view, status in zip(views, statuses, strict=False)]

    report = build_run_report(views, results, [], [], [], "Done", NOW)

    assert report.counts.model_dump() == {
        "total": 6,
        "passed": 2,
        "failed": 1,
        "blocked": 1,
        "skipped": 1,
        "not_reported": 1,
    }
    assert report.summary == "Done"
    assert report.built_at == NOW


def test_failed_cases_follow_the_run_order_with_the_first_failing_step() -> None:
    first_view, second_view, third_view = build_view(1), build_view(2), build_view(3)
    blocked = build_result(third_view, ResultStatus.BLOCKED)
    failed = build_result(first_view, ResultStatus.FAILED)
    passed = build_result(second_view, ResultStatus.PASSED)
    steps = [
        build_step(failed.id, 1, ResultStatus.PASSED),
        build_step(failed.id, 3, ResultStatus.FAILED, "Late error"),
        build_step(failed.id, 2, ResultStatus.BLOCKED, "Spinner"),
    ]
    missing = [
        MissingScreenshot(case_result_id=failed.id, test_case_id=first_view.test_case_id, code="TC-1", step_order=2)
    ]

    report = build_run_report(
        [third_view, first_view, second_view], [blocked, failed, passed], steps, [], missing, None, NOW
    )

    assert [(case.code, case.status) for case in report.failed_cases] == [
        ("TC-1", ResultStatus.FAILED),
        ("TC-3", ResultStatus.BLOCKED),
    ]
    first_failed = report.failed_cases[0]
    assert (first_failed.title, first_failed.step_order, first_failed.step_action) == ("Case 1", 2, "Action 2")
    assert (first_failed.actual_result, first_failed.error) == ("Saw 2", "Spinner")
    assert report.failed_cases[1].step_order is None
    assert report.failed_cases[1].step_action is None
    assert report.missing_screenshots == missing


@pytest.mark.parametrize(
    ("statuses", "expected"),
    [
        ([], (RunStatus.ABORTED, RunAbortReason.NO_RESULTS)),
        ([ResultStatus.PASSED, ResultStatus.FAILED], (RunStatus.FAILED, None)),
        ([ResultStatus.BLOCKED], (RunStatus.FAILED, None)),
        ([ResultStatus.PASSED, ResultStatus.SKIPPED], (RunStatus.PASSED, None)),
        ([ResultStatus.SKIPPED, ResultStatus.SKIPPED], (RunStatus.PASSED, None)),
    ],
)
def test_finished_status_follows_the_results(
    statuses: list[ResultStatus], expected: tuple[RunStatus, RunAbortReason | None]
) -> None:
    results = [build_result(build_view(position), status) for position, status in enumerate(statuses, start=1)]

    assert resolve_finished_status(results) == expected

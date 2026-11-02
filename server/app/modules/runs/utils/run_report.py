from datetime import datetime
from uuid import UUID

from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.criterion_impact.entity import CriterionImpact
from app.modules.runs.domains.failed_case_report.entity import FailedCaseReport
from app.modules.runs.domains.missing_screenshot.entity import MissingScreenshot
from app.modules.runs.domains.run_case_view.entity import RunCaseView
from app.modules.runs.domains.run_report.entity import RunReport
from app.modules.runs.domains.run_report_story.entity import RunReportStory
from app.modules.runs.domains.skipped_run_case.entity import SkippedRunCase
from app.modules.runs.domains.step_result.entity import StepResult
from app.modules.runs.typing.constants.run_report import FAILING_RESULT_STATUSES
from app.modules.runs.utils.run_counts import build_run_counts
from app.modules.runs.utils.worst_iteration import select_worst_results


def build_run_report(
    run_cases: list[RunCaseView],
    case_results: list[CaseResult],
    step_results: list[StepResult],
    criterion_impacts: list[CriterionImpact],
    missing_screenshots: list[MissingScreenshot],
    summary: str | None,
    now: datetime,
    skipped_cases: list[SkippedRunCase] | None = None,
) -> RunReport:
    run_case_ids = {run_case.test_case_id for run_case in run_cases}
    results_by_case_id = select_worst_results(
        case_result for case_result in case_results if case_result.test_case_id in run_case_ids
    )
    return RunReport(
        counts=build_run_counts(len(run_cases), [case_result.status for case_result in results_by_case_id.values()]),
        failed_cases=[
            build_failed_case_report(run_case, case_result, step_results)
            for run_case in sorted(run_cases, key=lambda view: view.position)
            if (case_result := results_by_case_id.get(run_case.test_case_id)) is not None
            and case_result.status in FAILING_RESULT_STATUSES
        ],
        criterion_impacts=criterion_impacts,
        missing_screenshots=missing_screenshots,
        summary=summary,
        built_at=now,
        stories=build_story_reports(run_cases, results_by_case_id),
        skipped_cases=skipped_cases or [],
    )


def build_story_reports(
    run_cases: list[RunCaseView], results_by_case_id: dict[UUID, CaseResult]
) -> list[RunReportStory]:
    cases_by_story_id: dict[UUID, list[RunCaseView]] = {}
    for run_case in sorted(run_cases, key=lambda view: view.position):
        if run_case.story_id is not None:
            cases_by_story_id.setdefault(run_case.story_id, []).append(run_case)
    return [
        RunReportStory(
            story_id=story_id,
            story_jira_key=story_cases[0].story_jira_key or "",
            story_title=story_cases[0].story_title or "",
            counts=build_run_counts(
                len(story_cases),
                [
                    case_result.status
                    for story_case in story_cases
                    if (case_result := results_by_case_id.get(story_case.test_case_id)) is not None
                ],
            ),
        )
        for story_id, story_cases in cases_by_story_id.items()
    ]


def build_failed_case_report(
    run_case: RunCaseView, case_result: CaseResult, step_results: list[StepResult]
) -> FailedCaseReport:
    failing_steps = sorted(
        (
            step_result
            for step_result in step_results
            if step_result.case_result_id == case_result.id and step_result.status in FAILING_RESULT_STATUSES
        ),
        key=lambda step_result: step_result.step_order,
    )
    first_failing_step = failing_steps[0] if failing_steps else None
    version_step = (
        None
        if first_failing_step is None
        else next((step for step in run_case.version.steps if step.order == first_failing_step.step_order), None)
    )
    return FailedCaseReport(
        test_case_id=run_case.test_case_id,
        code=run_case.code,
        title=run_case.version.title,
        status=case_result.status,
        step_order=None if first_failing_step is None else first_failing_step.step_order,
        step_action=None if version_step is None else version_step.action,
        actual_result=None if first_failing_step is None else first_failing_step.actual_result,
        error=None if first_failing_step is None else first_failing_step.error,
        suspected_cause=case_result.suspected_cause,
        cause_reason=case_result.cause_reason,
        story_jira_key=run_case.story_jira_key,
    )

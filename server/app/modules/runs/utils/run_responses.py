from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_case_detail.entity import RunCaseDetail
from app.modules.runs.domains.run_counts.entity import RunCounts
from app.modules.runs.domains.run_detail.entity import RunDetail
from app.modules.runs.domains.run_labels.entity import RunLabels
from app.modules.runs.domains.run_report.entity import RunReport
from app.modules.runs.domains.run_summary.entity import RunSummary
from app.modules.runs.domains.step_result_view.entity import StepResultView
from app.modules.runs.models.run_case_response import RunCaseResponse
from app.modules.runs.models.run_case_result_response import RunCaseResultResponse
from app.modules.runs.models.run_counts_response import RunCountsResponse
from app.modules.runs.models.run_detail_response import RunDetailResponse
from app.modules.runs.models.run_report_response import RunReportResponse
from app.modules.runs.models.run_summary_response import RunSummaryResponse
from app.modules.runs.models.step_result_response import StepResultResponse
from app.modules.runs.utils.run_counts import build_run_counts


def build_run_summary_response(summary: RunSummary) -> RunSummaryResponse:
    return RunSummaryResponse.model_validate(build_summary_fields(summary.run, summary.labels, summary.counts))


def build_run_detail_response(detail: RunDetail) -> RunDetailResponse:
    counts = build_run_counts(
        len(detail.cases), [case.result.status for case in detail.cases if case.result is not None]
    )
    return RunDetailResponse.model_validate(
        {
            **build_summary_fields(detail.run, detail.labels, counts),
            "summary": detail.run.summary,
            "report": None if detail.run.report is None else build_run_report_response(detail.run.report),
            "child_run_ids": detail.child_run_ids,
            "cases": [build_run_case_response(case) for case in detail.cases],
        }
    )


def build_summary_fields(run: Run, labels: RunLabels, counts: RunCounts) -> dict[str, object]:
    return {
        "id": run.id,
        "story_id": run.story_id,
        "story_jira_key": labels.story_jira_key,
        "story_title": labels.story_title,
        "environment_id": run.environment_id,
        "environment_name": labels.environment_name,
        "executor": run.executor,
        "status": run.status,
        "abort_reason": run.abort_reason,
        "parent_run_id": run.parent_run_id,
        "started_by": run.started_by,
        "started_by_name": labels.started_by_name,
        "started_at": run.started_at,
        "finished_at": run.finished_at,
        "counts": RunCountsResponse.model_validate(counts.model_dump()),
    }


def build_run_report_response(report: RunReport) -> RunReportResponse:
    return RunReportResponse.model_validate(report.model_dump())


def build_run_case_response(case: RunCaseDetail) -> RunCaseResponse:
    return RunCaseResponse(
        test_case_id=case.view.test_case_id,
        code=case.view.code,
        title=case.view.version.title,
        version_id=case.view.version.id,
        version_number=case.view.version.number,
        position=case.view.position,
        result=None
        if case.result is None
        else RunCaseResultResponse(
            id=case.result.id,
            status=case.result.status,
            duration_ms=case.result.duration_ms,
            recorded_at=case.result.created_at,
        ),
        steps=[build_step_result_response(step) for step in case.steps],
    )


def build_step_result_response(step: StepResultView) -> StepResultResponse:
    return StepResultResponse(
        order=step.step.order,
        action=step.step.action,
        expected=step.step.expected,
        status=None if step.result is None else step.result.status,
        actual_result=None if step.result is None else step.result.actual_result,
        error=None if step.result is None else step.result.error,
        screenshot_file_id=None if step.result is None else step.result.screenshot_file_id,
        screenshot_status=step.screenshot_status,
        evidence_file_id=None if step.result is None else step.result.evidence_file_id,
    )

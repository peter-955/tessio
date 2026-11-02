from app.modules.runs.domains.case_result.entity import CaseResult
from app.modules.runs.domains.junit_import.entity import JunitImport
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_case_detail.entity import RunCaseDetail
from app.modules.runs.domains.run_case_iteration.entity import RunCaseIteration
from app.modules.runs.domains.run_counts.entity import RunCounts
from app.modules.runs.domains.run_detail.entity import RunDetail
from app.modules.runs.domains.run_labels.entity import RunLabels
from app.modules.runs.domains.run_report.entity import RunReport
from app.modules.runs.domains.run_summary.entity import RunSummary
from app.modules.runs.domains.step_result_view.entity import StepResultView
from app.modules.runs.models.junit_import_response import JunitImportResponse
from app.modules.runs.models.run_case_file_response import RunCaseFileResponse
from app.modules.runs.models.run_case_iteration_response import RunCaseIterationResponse
from app.modules.runs.models.run_case_response import RunCaseResponse
from app.modules.runs.models.run_case_result_response import RunCaseResultResponse
from app.modules.runs.models.run_counts_response import RunCountsResponse
from app.modules.runs.models.run_criterion_response import RunCriterionResponse
from app.modules.runs.models.run_data_value_response import RunDataValueResponse
from app.modules.runs.models.run_detail_response import RunDetailResponse
from app.modules.runs.models.run_report_response import RunReportResponse
from app.modules.runs.models.run_summary_response import RunSummaryResponse
from app.modules.runs.models.step_diagnosis_response import StepDiagnosisResponse
from app.modules.runs.models.step_result_response import StepResultResponse
from app.modules.runs.models.unmapped_test_response import UnmappedTestResponse
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
            "environment_base_url": detail.labels.environment_base_url,
            "summary": detail.run.summary,
            "report": None if detail.run.report is None else build_run_report_response(detail.run.report),
            "child_run_ids": detail.child_run_ids,
            "cases": [build_run_case_response(case) for case in detail.cases],
            "data": [RunDataValueResponse.model_validate(value.model_dump()) for value in detail.data],
            "skipped_cases": [skipped_case.model_dump() for skipped_case in detail.run.skipped_cases or []],
        }
    )


def build_summary_fields(run: Run, labels: RunLabels, counts: RunCounts) -> dict[str, object]:
    return {
        "id": run.id,
        "story_id": run.story_id,
        "story_jira_key": labels.story_jira_key,
        "story_title": labels.story_title,
        "test_suite_id": run.test_suite_id,
        "test_suite_name": labels.test_suite_name,
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
        story_id=case.view.story_id,
        story_jira_key=case.view.story_jira_key,
        story_title=case.view.story_title,
        business_value=case.view.version.business_value,
        preconditions=case.view.version.preconditions,
        criteria=[RunCriterionResponse.model_validate(criterion.model_dump()) for criterion in case.criteria],
        files=[RunCaseFileResponse.model_validate(case_file.model_dump()) for case_file in case.files],
        result=build_case_result_response(case.result),
        steps=[build_step_result_response(step) for step in case.steps],
        parameters=case.view.version.parameters,
        iterations=[build_iteration_response(iteration) for iteration in case.iterations],
    )


def build_case_result_response(case_result: CaseResult | None) -> RunCaseResultResponse | None:
    if case_result is None:
        return None
    return RunCaseResultResponse(
        id=case_result.id,
        status=case_result.status,
        duration_ms=case_result.duration_ms,
        suspected_cause=case_result.suspected_cause,
        cause_reason=case_result.cause_reason,
        recorded_at=case_result.created_at,
        iteration=case_result.iteration,
    )


def build_iteration_response(iteration: RunCaseIteration) -> RunCaseIterationResponse:
    return RunCaseIterationResponse(
        iteration=iteration.iteration,
        values=iteration.values,
        result=build_case_result_response(iteration.result),
        steps=[build_step_result_response(step) for step in iteration.steps],
    )


def build_step_result_response(step: StepResultView) -> StepResultResponse:
    return StepResultResponse(
        order=step.step.order,
        action=step.step.action or "",
        expected=step.step.expected,
        status=None if step.result is None else step.result.status,
        actual_result=None if step.result is None else step.result.actual_result,
        error=None if step.result is None else step.result.error,
        screenshot_file_id=None if step.result is None else step.result.screenshot_file_id,
        screenshot_status=step.screenshot_status,
        evidence_file_id=None if step.result is None else step.result.evidence_file_id,
        diagnosis=None
        if step.result is None or step.result.diagnosis is None
        else StepDiagnosisResponse.model_validate(step.result.diagnosis.model_dump()),
    )


def build_junit_import_response(junit_import: JunitImport) -> JunitImportResponse:
    return JunitImportResponse(
        run_id=junit_import.run.id,
        status=junit_import.run.status,
        counts=RunCountsResponse.model_validate(junit_import.counts.model_dump()),
        mapped_test_count=junit_import.mapped_test_count,
        unmapped_test_count=junit_import.unmapped_test_count,
        unmapped_tests=[
            UnmappedTestResponse.model_validate(unmapped_test.model_dump())
            for unmapped_test in junit_import.unmapped_tests
        ],
    )

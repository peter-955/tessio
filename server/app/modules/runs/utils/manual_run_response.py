from app.modules.runs.domains.recorded_manual_case_result.entity import RecordedManualCaseResult
from app.modules.runs.domains.run.entity import Run
from app.modules.runs.domains.run_sheet.entity import RunSheet
from app.modules.runs.models.manual_case_result_response import ManualCaseResultResponse
from app.modules.runs.models.manual_run_case_response import ManualRunCaseResponse
from app.modules.runs.models.manual_run_response import ManualRunResponse
from app.modules.runs.models.manual_run_step_response import ManualRunStepResponse
from app.modules.runs.models.manual_step_result_response import ManualStepResultResponse
from app.modules.runs.models.skipped_run_case_response import SkippedRunCaseResponse
from app.modules.runs.utils.worst_iteration import select_worst_results


def build_manual_run_response(run_source: RunSheet | Run) -> ManualRunResponse:
    run = run_source.run if isinstance(run_source, RunSheet) else run_source
    cases: list[ManualRunCaseResponse] = []
    if isinstance(run_source, RunSheet):
        result_statuses = {
            test_case_id: case_result.status
            for test_case_id, case_result in select_worst_results(run_source.case_results).items()
        }
        cases = [
            ManualRunCaseResponse(
                test_case_id=version.test_case_id,
                test_case_version_id=version.id,
                title=version.title,
                steps=[
                    ManualRunStepResponse(
                        order=step.order,
                        action=step.action or "",
                        expected=step.expected,
                    )
                    for step in version.steps
                ],
                result_status=result_statuses.get(version.test_case_id),
                parameters=version.parameters,
                data_rows=version.data_rows,
            )
            for version in run_source.case_versions
        ]
    return ManualRunResponse(
        id=run.id,
        story_id=run.story_id,
        test_suite_id=run.test_suite_id,
        environment_id=run.environment_id,
        executor=run.executor,
        status=run.status,
        parent_run_id=run.parent_run_id,
        started_by=run.started_by,
        started_at=run.started_at,
        finished_at=run.finished_at,
        abort_reason=run.abort_reason,
        summary=run.summary,
        cases=cases,
        skipped_cases=[
            SkippedRunCaseResponse.model_validate(skipped_case.model_dump()) for skipped_case in run.skipped_cases or []
        ],
    )


def build_manual_case_result_response(recorded: RecordedManualCaseResult) -> ManualCaseResultResponse:
    case_result = recorded.case_result
    return ManualCaseResultResponse(
        id=case_result.id,
        run_id=case_result.run_id,
        test_case_id=case_result.test_case_id,
        status=case_result.status,
        suggested_status=recorded.suggested_status,
        duration_ms=case_result.duration_ms,
        iteration=case_result.iteration,
        steps=[
            ManualStepResultResponse(
                order=step_result.step_order,
                status=step_result.status,
                actual_result=step_result.actual_result or "",
                error=step_result.error,
                evidence_file_id=step_result.evidence_file_id,
            )
            for step_result in recorded.step_results
        ],
    )

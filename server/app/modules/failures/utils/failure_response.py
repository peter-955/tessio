from app.modules.failures.domains.failure_detail.entity import FailureDetail
from app.modules.failures.domains.failure_view.entity import FailureView
from app.modules.failures.models.failed_step_response import FailedStepResponse
from app.modules.failures.models.failure_detail_response import FailureDetailResponse
from app.modules.failures.models.failure_event_response import FailureEventResponse
from app.modules.failures.models.failure_response import FailureResponse
from app.modules.failures.models.failure_result_response import FailureResultResponse


def build_failure_response(view: FailureView) -> FailureResponse:
    failure = view.failure
    return FailureResponse(
        id=failure.id,
        project_key=view.project_key,
        story_id=failure.story_id,
        story_jira_key=view.story_jira_key,
        story_title=view.story_title,
        test_case_id=failure.test_case_id,
        test_case_code=view.test_case_code,
        test_case_title=view.test_case_title,
        status=failure.status,
        is_active=failure.is_active,
        assignee_id=failure.assignee_id,
        assignee_name=view.assignee_name,
        assignee_status=view.assignee_status,
        opened_by_case_result_id=failure.opened_by_case_result_id,
        latest_case_result_id=failure.latest_case_result_id,
        latest_run_id=view.latest_run_id,
        latest_failed_at=view.latest_failed_at,
        status_changed_at=failure.status_changed_at,
        status_changed_by_name=view.status_changed_by_name,
        created_at=failure.created_at,
    )


def build_failure_detail_response(detail: FailureDetail) -> FailureDetailResponse:
    failed_step = detail.failed_step
    return FailureDetailResponse(
        **build_failure_response(detail.view).model_dump(),
        failed_step=None
        if failed_step is None
        else FailedStepResponse(
            step_order=failed_step.step_order,
            actual_result=failed_step.actual_result,
            error=failed_step.error,
            screenshot_file_id=failed_step.screenshot_file_id,
        ),
        results=[
            FailureResultResponse(
                case_result_id=result.case_result_id,
                run_id=result.run_id,
                run_status=result.run_status,
                run_executor=result.run_executor,
                status=result.status,
                duration_ms=result.duration_ms,
                recorded_at=result.recorded_at,
                started_by_name=result.started_by_name,
            )
            for result in detail.results
        ],
        events=[
            FailureEventResponse(
                id=event_view.event.id,
                kind=event_view.event.kind,
                from_status=event_view.event.from_status,
                to_status=event_view.event.to_status,
                case_result_id=event_view.event.case_result_id,
                run_id=event_view.run_id,
                assignee_id=event_view.event.assignee_id,
                assignee_name=event_view.assignee_name,
                actor_id=event_view.event.actor_id,
                actor_name=event_view.actor_name,
                created_at=event_view.event.created_at,
            )
            for event_view in detail.events
        ],
    )

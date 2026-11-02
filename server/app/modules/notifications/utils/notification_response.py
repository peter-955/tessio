from app.modules.notifications.domains.notification_list_item.entity import NotificationListItem
from app.modules.notifications.domains.notification_payload.entity import (
    FailureAssignedPayload,
    GapAssignedPayload,
    NotificationPayload,
    ReportReadyPayload,
    RunFinishedPayload,
    SuiteRunFinishedPayload,
)
from app.modules.notifications.models.failure_assigned_payload_response import FailureAssignedPayloadResponse
from app.modules.notifications.models.gap_assigned_payload_response import GapAssignedPayloadResponse
from app.modules.notifications.models.notification_response import NotificationResponse
from app.modules.notifications.models.report_ready_payload_response import ReportReadyPayloadResponse
from app.modules.notifications.models.run_finished_payload_response import RunFinishedPayloadResponse
from app.modules.notifications.models.suite_run_finished_payload_response import SuiteRunFinishedPayloadResponse


def build_payload_response(
    payload: NotificationPayload,
) -> (
    GapAssignedPayloadResponse
    | FailureAssignedPayloadResponse
    | RunFinishedPayloadResponse
    | SuiteRunFinishedPayloadResponse
    | ReportReadyPayloadResponse
):
    match payload:
        case GapAssignedPayload():
            return GapAssignedPayloadResponse(
                kind=payload.kind,
                gap_id=payload.gap_id,
                story_id=payload.story_id,
                story_jira_key=payload.story_jira_key,
                question=payload.question,
            )
        case FailureAssignedPayload():
            return FailureAssignedPayloadResponse(
                kind=payload.kind,
                failure_id=payload.failure_id,
                test_case_id=payload.test_case_id,
                test_case_code=payload.test_case_code,
                test_case_title=payload.test_case_title,
                story_jira_key=payload.story_jira_key,
            )
        case RunFinishedPayload():
            return RunFinishedPayloadResponse(
                kind=payload.kind,
                run_id=payload.run_id,
                story_id=payload.story_id,
                story_jira_key=payload.story_jira_key,
                outcome=payload.outcome,
                passed_count=payload.passed_count,
                failed_count=payload.failed_count,
                blocked_count=payload.blocked_count,
            )
        case SuiteRunFinishedPayload():
            return SuiteRunFinishedPayloadResponse(
                kind=payload.kind,
                run_id=payload.run_id,
                test_suite_id=payload.test_suite_id,
                test_suite_name=payload.test_suite_name,
                outcome=payload.outcome,
                passed_count=payload.passed_count,
                failed_count=payload.failed_count,
                blocked_count=payload.blocked_count,
            )
        case ReportReadyPayload():
            return ReportReadyPayloadResponse(
                kind=payload.kind,
                file_id=payload.file_id,
                file_name=payload.file_name,
                format=payload.format,
                source=payload.source,
                source_id=payload.source_id,
                source_label=payload.source_label,
            )


def build_notification_response(item: NotificationListItem) -> NotificationResponse:
    notification = item.notification
    return NotificationResponse(
        id=notification.id,
        kind=notification.kind,
        project_id=notification.project_id,
        project_key=item.project_key,
        project_name=item.project_name,
        actor_id=notification.actor_id,
        actor_name=item.actor_name,
        payload=build_payload_response(notification.payload),
        is_read=notification.is_read,
        read_at=notification.read_at,
        created_at=notification.created_at,
    )

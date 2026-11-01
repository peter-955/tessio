import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.runs import RunAbortReason, RunReport, RunStatus
from app.modules.runs.domains.run_counts.entity import RunCounts
from app.shared.events import LiveEventType
from app.shared.masking import MASKED_VALUE
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.runs.manual.manual_run_steps import (
    SECRET_VALUE,
    find_run_row,
    finish_manual_run,
    list_run_notifications,
    record_case_status,
    seed_manual_run_project,
    sign_up_account,
    start_manual_run_id,
)
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


@pytest.mark.parametrize(
    ("case_statuses", "run_status"),
    [
        (["passed", "failed", "passed"], "failed"),
        (["passed", "blocked"], "failed"),
        (["skipped", "skipped", "skipped"], "passed"),
        (["passed", "passed"], "passed"),
    ],
)
async def test_finish_status_follows_case_results(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    case_statuses: list[str],
    run_status: str,
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    for case, case_status in zip(seeded.cases, case_statuses, strict=False):
        await record_case_status(client, seeded.key, run_id, case.id, case_status)

    response = await finish_manual_run(client, seeded.key, run_id)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == run_status
    assert body["abortReason"] is None
    assert body["finishedAt"] is not None
    assert body["cases"] == []


async def test_finish_without_results_aborts(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)

    response = await finish_manual_run(client, seeded.key, run_id)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "aborted"
    assert body["abortReason"] == "no_results"
    run_row = await find_run_row(container, run_id)
    assert run_row.status is RunStatus.ABORTED
    assert run_row.abort_reason is RunAbortReason.NO_RESULTS


async def test_finish_masks_summary_and_saves_report(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    await record_case_status(client, seeded.key, run_id, seeded.cases[0].id, "passed")
    await record_case_status(client, seeded.key, run_id, seeded.cases[1].id, "failed")

    response = await finish_manual_run(client, seeded.key, run_id, summary=f"Login with {SECRET_VALUE} failed")

    assert response.status_code == 200, response.text
    assert response.json()["summary"] == f"Login with {MASKED_VALUE} failed"
    run_row = await find_run_row(container, run_id)
    assert run_row.summary == f"Login with {MASKED_VALUE} failed"
    assert run_row.finished_at is not None
    assert run_row.last_activity_at == run_row.finished_at
    report = RunReport.model_validate(run_row.report)
    assert report.counts == RunCounts(total=3, passed=1, failed=1, blocked=0, skipped=0, not_reported=1)
    assert report.summary == f"Login with {MASKED_VALUE} failed"
    assert [failed_case.test_case_id for failed_case in report.failed_cases] == [seeded.cases[1].id]
    assert report.missing_screenshots == []


async def test_finish_notifies_starter_and_qc_members(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    other_qc = await sign_up_account(client, container, recording_mailer, seeded.project, ProjectRole.QC, "Other QC")
    project_manager = await sign_up_account(client, container, recording_mailer, seeded.project, ProjectRole.PM, "Pam")
    developer = await sign_up_account(client, container, recording_mailer, seeded.project, ProjectRole.DEV, "Dev")
    use_session(client, seeded.qc.session_token)
    run_id = await start_manual_run_id(client, seeded)
    await record_case_status(client, seeded.key, run_id, seeded.cases[0].id, "failed")
    await record_case_status(client, seeded.key, run_id, seeded.cases[1].id, "blocked")

    response = await finish_manual_run(client, seeded.key, run_id)

    assert response.status_code == 200, response.text
    notifications = await list_run_notifications(container, seeded.project, run_id)
    notified_user_ids = {notification.user_id for notification in notifications}
    assert notified_user_ids == {seeded.qc.user_id, other_qc.user_id}
    assert project_manager.user_id not in notified_user_ids
    assert developer.user_id not in notified_user_ids
    payload = notifications[0].payload
    assert payload["kind"] == "run_finished"
    assert payload["story_jira_key"] == seeded.story_key
    assert payload["outcome"] == "failed"
    assert payload["passed_count"] == 0
    assert payload["failed_count"] == 1
    assert payload["blocked_count"] == 1
    assert all(notification.actor_id == seeded.qc.user_id for notification in notifications)
    finished_events = [
        event for event in recording_live_event_publisher.events if event.type is LiveEventType.RUN_FINISHED
    ]
    assert len(finished_events) == 1
    assert finished_events[0].ids == {"runId": run_id, "storyId": str(seeded.story_id), "status": "failed"}


async def test_second_finish_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    first_response = await finish_manual_run(client, seeded.key, run_id)
    assert first_response.status_code == 200, first_response.text

    response = await finish_manual_run(client, seeded.key, run_id)

    assert response.status_code == 409
    assert response.json()["code"] == "RUN_NOT_RUNNING"


async def test_another_qc_cannot_finish(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    await sign_up_account(client, container, recording_mailer, seeded.project, ProjectRole.QC, "Other QC")

    response = await finish_manual_run(client, seeded.key, run_id)

    assert response.status_code == 403
    assert response.json()["code"] == "RUN_NOT_OWNED"

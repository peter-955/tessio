from datetime import UTC, datetime, timedelta

from httpx import AsyncClient

from app.container import Container
from app.modules.runs import RunAbortReason, RunReport, RunStatus
from app.modules.runs.domains.run_counts.entity import RunCounts
from app.shared.events import LiveEventType
from tests.api.runs.manual.manual_run_steps import (
    find_run_row,
    finish_manual_run,
    list_run_notifications,
    move_last_activity_back,
    record_case_status,
    seed_manual_run_project,
    start_manual_run_id,
)
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_idle_run_is_aborted_with_partial_report(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    await container.abort_stale_runs.execute(datetime.now(UTC))
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    await record_case_status(client, seeded.key, run_id, seeded.cases[0].id, "passed")
    await record_case_status(client, seeded.key, run_id, seeded.cases[1].id, "failed")
    await move_last_activity_back(container, run_id, timedelta(hours=5))
    recording_live_event_publisher.events.clear()

    aborted_count = await container.abort_stale_runs.execute(datetime.now(UTC))

    assert aborted_count == 1
    run_row = await find_run_row(container, run_id)
    assert run_row.status is RunStatus.ABORTED
    assert run_row.abort_reason is RunAbortReason.INACTIVE
    assert run_row.finished_at is not None
    assert run_row.summary is None
    assert RunReport.model_validate(run_row.report).counts == RunCounts(
        total=3, passed=1, failed=1, blocked=0, skipped=0, not_reported=1
    )
    notifications = await list_run_notifications(container, seeded.project, run_id)
    assert {notification.user_id for notification in notifications} == {seeded.qc.user_id}
    assert all(notification.actor_id is None for notification in notifications)
    assert notifications[0].payload["outcome"] == "aborted"
    assert notifications[0].payload["passed_count"] == 1
    assert notifications[0].payload["failed_count"] == 1
    finished_events = [
        event for event in recording_live_event_publisher.events if event.type is LiveEventType.RUN_FINISHED
    ]
    assert [event.ids for event in finished_events] == [
        {"runId": run_id, "storyId": str(seeded.story_id), "status": "aborted"}
    ]


async def test_recent_and_finished_runs_are_untouched(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    await container.abort_stale_runs.execute(datetime.now(UTC))
    recent = await seed_manual_run_project(client, container, recording_mailer)
    recent_run_id = await start_manual_run_id(client, recent)
    await move_last_activity_back(container, recent_run_id, timedelta(hours=3))
    finished = await seed_manual_run_project(client, container, recording_mailer)
    finished_run_id = await start_manual_run_id(client, finished)
    await record_case_status(client, finished.key, finished_run_id, finished.cases[0].id, "passed")
    finish_response = await finish_manual_run(client, finished.key, finished_run_id)
    assert finish_response.status_code == 200, finish_response.text
    await move_last_activity_back(container, finished_run_id, timedelta(hours=5))
    stale = await seed_manual_run_project(client, container, recording_mailer)
    stale_run_id = await start_manual_run_id(client, stale)
    await move_last_activity_back(container, stale_run_id, timedelta(hours=4, minutes=1))

    aborted_count = await container.abort_stale_runs.execute(datetime.now(UTC))

    assert aborted_count == 1
    assert (await find_run_row(container, recent_run_id)).status is RunStatus.RUNNING
    finished_row = await find_run_row(container, finished_run_id)
    assert finished_row.status is RunStatus.PASSED
    assert finished_row.abort_reason is None
    stale_row = await find_run_row(container, stale_run_id)
    assert stale_row.status is RunStatus.ABORTED
    assert RunReport.model_validate(stale_row.report).counts.not_reported == 3
    assert await container.abort_stale_runs.execute(datetime.now(UTC)) == 0

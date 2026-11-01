from datetime import UTC, datetime, timedelta
from uuid import uuid4

from httpx import AsyncClient

from app.container import Container
from app.modules.runs import RunStatus
from app.modules.test_cases import TestCaseStatus as CaseStatus
from app.shared.events import LiveEventType
from tests.api.runs.manual.manual_run_steps import (
    ManualRunProject,
    change_case_status,
    find_run_row,
    finish_manual_run,
    move_last_activity_back,
    record_case_status,
    rerun_failed_cases,
    seed_environment,
    seed_manual_run_project,
    start_manual_run_id,
)
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def finish_run_with(client: AsyncClient, seeded: ManualRunProject, case_statuses: list[str]) -> str:
    run_id = await start_manual_run_id(client, seeded)
    for case, case_status in zip(seeded.cases, case_statuses, strict=False):
        await record_case_status(client, seeded.key, run_id, case.id, case_status)
    response = await finish_manual_run(client, seeded.key, run_id)
    assert response.status_code == 200, response.text
    return run_id


async def test_rerun_keeps_failed_and_blocked_cases(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    seeded = await seed_manual_run_project(
        client,
        container,
        recording_mailer,
        (CaseStatus.READY, CaseStatus.READY, CaseStatus.READY, CaseStatus.READY),
    )
    parent_run_id = await finish_run_with(client, seeded, ["blocked", "passed", "failed", "skipped"])
    await seed_environment(container, seeded.project, "production")

    response = await rerun_failed_cases(client, seeded.key, parent_run_id)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["parentRunId"] == parent_run_id
    assert body["executor"] == "manual"
    assert body["status"] == "running"
    assert body["environmentId"] == str(seeded.environment_id)
    assert [case["testCaseId"] for case in body["cases"]] == [str(seeded.cases[0].id), str(seeded.cases[2].id)]
    started_events = [
        event for event in recording_live_event_publisher.events if event.type is LiveEventType.RUN_STARTED
    ]
    assert started_events[-1].ids == {
        "runId": body["id"],
        "storyId": str(seeded.story_id),
        "parentRunId": parent_run_id,
    }


async def test_rerun_can_pick_another_environment(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    parent_run_id = await finish_run_with(client, seeded, ["failed"])
    production_id = await seed_environment(container, seeded.project, "production")

    response = await rerun_failed_cases(client, seeded.key, parent_run_id, environmentId=str(production_id))

    assert response.status_code == 201, response.text
    assert response.json()["environmentId"] == str(production_id)


async def test_rerun_of_passed_run_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    parent_run_id = await finish_run_with(client, seeded, ["passed", "passed", "skipped"])

    response = await rerun_failed_cases(client, seeded.key, parent_run_id)

    assert response.status_code == 409
    assert response.json()["code"] == "NO_FAILED_CASES_TO_RERUN"


async def test_rerun_skips_cases_that_are_no_longer_ready(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    parent_run_id = await finish_run_with(client, seeded, ["failed", "passed", "passed"])
    await change_case_status(container, seeded.cases[0].id, CaseStatus.DEPRECATED)

    response = await rerun_failed_cases(client, seeded.key, parent_run_id)

    assert response.status_code == 409
    assert response.json()["code"] == "NO_FAILED_CASES_TO_RERUN"


async def test_rerun_of_aborted_run_is_allowed(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    parent_run_id = await start_manual_run_id(client, seeded)
    await record_case_status(client, seeded.key, parent_run_id, seeded.cases[1].id, "failed")
    await move_last_activity_back(container, parent_run_id, timedelta(hours=5))
    await container.abort_stale_runs.execute(datetime.now(UTC))
    assert (await find_run_row(container, parent_run_id)).status is RunStatus.ABORTED

    response = await rerun_failed_cases(client, seeded.key, parent_run_id)

    assert response.status_code == 201, response.text
    assert [case["testCaseId"] for case in response.json()["cases"]] == [str(seeded.cases[1].id)]


async def test_rerun_of_run_without_results_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    parent_run_id = await finish_run_with(client, seeded, [])

    response = await rerun_failed_cases(client, seeded.key, parent_run_id)

    assert response.status_code == 409
    assert response.json()["code"] == "NO_FAILED_CASES_TO_RERUN"


async def test_rerun_of_running_run_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    await record_case_status(client, seeded.key, run_id, seeded.cases[0].id, "failed")

    response = await rerun_failed_cases(client, seeded.key, run_id)

    assert response.status_code == 409
    assert response.json()["code"] == "RUN_NOT_FINISHED"


async def test_rerun_of_unknown_run_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)

    response = await rerun_failed_cases(client, seeded.key, str(uuid4()))

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"

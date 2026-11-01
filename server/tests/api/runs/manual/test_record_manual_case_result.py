from uuid import uuid4

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.files import StoredFileKind, StoredFileStatus
from app.modules.runs import ResultStatus
from app.modules.test_cases import TestCaseStatus as CaseStatus
from app.shared.events import LiveEventType
from app.shared.masking import MASKED_VALUE
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.runs.manual.manual_run_steps import (
    SECRET_VALUE,
    build_step,
    find_run_row,
    finish_manual_run,
    record_case,
    seed_claude_run,
    seed_evidence_file,
    seed_manual_run_project,
    sign_up_account,
    start_manual_run_id,
)
from tests.api.runs.recording_case_result_recorded_handler import RecordingCaseResultRecordedHandler
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


@pytest.mark.parametrize(
    ("step_statuses", "suggested_status"),
    [
        (["passed", "passed", "passed"], "passed"),
        (["passed", "failed", "blocked"], "failed"),
        (["blocked", "passed", "skipped"], "blocked"),
        (["passed"], "passed"),
        (["skipped", "skipped", "skipped"], "skipped"),
        ([], "skipped"),
    ],
)
async def test_suggested_status_follows_step_results(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    step_statuses: list[str],
    suggested_status: str,
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)

    response = await record_case(
        client,
        seeded.key,
        run_id,
        seeded.cases[0].id,
        steps=[build_step(order, status) for order, status in enumerate(step_statuses, start=1)],
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["suggestedStatus"] == suggested_status
    assert body["status"] == suggested_status


async def test_tester_overrides_suggestion_and_unreported_steps_are_skipped(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)

    response = await record_case(
        client,
        seeded.key,
        run_id,
        seeded.cases[0].id,
        status="passed",
        durationMs=1200,
        steps=[build_step(2, "failed", actualResult="Button greyed out", error="Timeout")],
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "passed"
    assert body["suggestedStatus"] == "failed"
    assert body["durationMs"] == 1200
    assert body["runId"] == run_id
    assert body["testCaseId"] == str(seeded.cases[0].id)
    assert body["steps"] == [
        {"order": 1, "status": "skipped", "actualResult": "", "error": None, "evidenceFileId": None},
        {
            "order": 2,
            "status": "failed",
            "actualResult": "Button greyed out",
            "error": "Timeout",
            "evidenceFileId": None,
        },
        {"order": 3, "status": "skipped", "actualResult": "", "error": None, "evidenceFileId": None},
    ]


async def test_secret_values_are_masked(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)

    response = await record_case(
        client,
        seeded.key,
        run_id,
        seeded.cases[0].id,
        steps=[
            build_step(1, "failed", actualResult=f"Typed {SECRET_VALUE} in the field", error=f"Rejected {SECRET_VALUE}")
        ],
    )

    assert response.status_code == 200, response.text
    step = response.json()["steps"][0]
    assert step["actualResult"] == f"Typed {MASKED_VALUE} in the field"
    assert step["error"] == f"Rejected {MASKED_VALUE}"
    assert SECRET_VALUE not in response.text


async def test_uploaded_evidence_is_attached(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    evidence_file_id = await seed_evidence_file(container, seeded.project.id, seeded.qc.user_id)

    response = await record_case(
        client,
        seeded.key,
        run_id,
        seeded.cases[0].id,
        steps=[build_step(1, "passed", evidenceFileId=str(evidence_file_id))],
    )

    assert response.status_code == 200, response.text
    assert response.json()["steps"][0]["evidenceFileId"] == str(evidence_file_id)


async def test_pending_evidence_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    evidence_file_id = await seed_evidence_file(
        container, seeded.project.id, seeded.qc.user_id, status=StoredFileStatus.PENDING
    )

    response = await record_case(
        client,
        seeded.key,
        run_id,
        seeded.cases[0].id,
        steps=[build_step(1, "passed", evidenceFileId=str(evidence_file_id))],
    )

    assert response.status_code == 409
    assert response.json()["code"] == "UPLOAD_NOT_COMPLETED"


@pytest.mark.parametrize("mismatch", ["project", "kind", "uploader", "unknown"])
async def test_foreign_evidence_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, mismatch: str
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    other_project = await seed_project(container)
    other_user = await sign_up_account(client, container, recording_mailer, seeded.project, ProjectRole.QC)
    use_session(client, seeded.qc.session_token)
    run_id = await start_manual_run_id(client, seeded)
    if mismatch == "project":
        evidence_file_id = await seed_evidence_file(container, other_project.id, seeded.qc.user_id)
    elif mismatch == "kind":
        evidence_file_id = await seed_evidence_file(
            container, seeded.project.id, seeded.qc.user_id, kind=StoredFileKind.IMPORT
        )
    elif mismatch == "uploader":
        evidence_file_id = await seed_evidence_file(container, seeded.project.id, other_user.user_id)
    else:
        evidence_file_id = uuid4()

    response = await record_case(
        client,
        seeded.key,
        run_id,
        seeded.cases[0].id,
        steps=[build_step(1, "passed", evidenceFileId=str(evidence_file_id))],
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REQUEST"


async def test_duplicate_result_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    first_response = await record_case(client, seeded.key, run_id, seeded.cases[0].id, status="passed")
    assert first_response.status_code == 200, first_response.text

    response = await record_case(client, seeded.key, run_id, seeded.cases[0].id, status="failed")

    assert response.status_code == 409
    assert response.json()["code"] == "CASE_RESULT_EXISTS"


async def test_case_outside_run_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer, (CaseStatus.READY, CaseStatus.DRAFT))
    run_id = await start_manual_run_id(client, seeded)

    response = await record_case(client, seeded.key, run_id, seeded.cases[1].id, status="passed")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.parametrize("orders", [[1, 1], [4], [2, 9]])
async def test_bad_step_orders_are_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, orders: list[int]
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)

    response = await record_case(
        client, seeded.key, run_id, seeded.cases[0].id, steps=[build_step(order, "passed") for order in orders]
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REQUEST"


async def test_finished_run_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    finish_response = await finish_manual_run(client, seeded.key, run_id)
    assert finish_response.status_code == 200, finish_response.text

    response = await record_case(client, seeded.key, run_id, seeded.cases[0].id, status="passed")

    assert response.status_code == 409
    assert response.json()["code"] == "RUN_NOT_RUNNING"


async def test_claude_run_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    claude_run_id = await seed_claude_run(container, seeded)

    response = await record_case(client, seeded.key, str(claude_run_id), seeded.cases[0].id, status="passed")

    assert response.status_code == 409
    assert response.json()["code"] == "RUN_NOT_MANUAL"


async def test_unknown_run_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)

    response = await record_case(client, seeded.key, str(uuid4()), seeded.cases[0].id, status="passed")

    assert response.status_code == 404


async def test_another_qc_cannot_record(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    await sign_up_account(client, container, recording_mailer, seeded.project, ProjectRole.QC, "Other QC")

    response = await record_case(client, seeded.key, run_id, seeded.cases[0].id, status="passed")

    assert response.status_code == 403
    assert response.json()["code"] == "RUN_NOT_OWNED"


async def test_admin_can_record_on_another_starters_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    await sign_up_account(client, container, recording_mailer, seeded.project, ProjectRole.ADMIN, "Ada Admin")

    response = await record_case(client, seeded.key, run_id, seeded.cases[0].id, status="passed")

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "passed"
    run_row = await find_run_row(container, run_id)
    assert run_row.started_by == seeded.qc.user_id


async def test_recording_calls_handler_publishes_and_moves_activity(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
    recording_case_result_recorded_handler: RecordingCaseResultRecordedHandler,
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    started_row = await find_run_row(container, run_id)

    response = await record_case(
        client, seeded.key, run_id, seeded.cases[0].id, steps=[build_step(1, "failed", actualResult="Crashed")]
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert len(recording_case_result_recorded_handler.recorded) == 1
    recorded = recording_case_result_recorded_handler.recorded[0]
    assert str(recorded.case_result_id) == body["id"]
    assert str(recorded.run_id) == run_id
    assert recorded.story_id == seeded.story_id
    assert recorded.project_id == seeded.project.id
    assert recorded.test_case_id == seeded.cases[0].id
    assert recorded.status is ResultStatus.FAILED
    assert recorded.recorded_by == seeded.qc.user_id
    recorded_events = [
        event for event in recording_live_event_publisher.events if event.type is LiveEventType.RUN_CASE_RECORDED
    ]
    assert len(recorded_events) == 1
    assert recorded_events[0].ids["runId"] == run_id
    assert recorded_events[0].ids["caseResultId"] == body["id"]
    assert recorded_events[0].ids["testCaseId"] == str(seeded.cases[0].id)
    assert recorded_events[0].ids["status"] == "failed"
    recorded_row = await find_run_row(container, run_id)
    assert recorded_row.last_activity_at > started_row.last_activity_at

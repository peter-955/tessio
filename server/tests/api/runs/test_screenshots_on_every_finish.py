from datetime import UTC, datetime, timedelta
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select, update

from app.modules.files import StoredFileKind, StoredFileStatus
from app.modules.files.infrastructure import StoredFileTable
from app.modules.runs.infrastructure import CaseResultTable, StepResultTable
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.runs.manual.manual_run_steps import (
    build_step,
    finish_manual_run,
    move_last_activity_back,
    record_case,
    seed_evidence_file,
    seed_manual_run_project,
    start_manual_run_id,
)
from tests.api.runs.run_steps import record_case_id, seed_runnable_story, sign_up_runner, start_run_id
from tests.api.runs.runs_test_container import RunsTestContainer
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer


async def list_screenshot_files(runs_container: RunsTestContainer, case_result_id: str) -> list[tuple[str, str]]:
    async with runs_container.database.begin():
        stored_files = await runs_container.database.get_current_session().scalars(
            select(StoredFileTable)
            .join(StepResultTable, StepResultTable.screenshot_file_id == StoredFileTable.id)
            .where(StepResultTable.case_result_id == UUID(case_result_id))
            .order_by(StepResultTable.step_order)
        )
        return [(stored_file.status.value, stored_file.object_key) for stored_file in stored_files]


async def find_file_status(runs_container: RunsTestContainer, file_id: UUID) -> StoredFileStatus:
    async with runs_container.database.begin():
        status = await runs_container.database.get_current_session().scalar(
            select(StoredFileTable.status).where(StoredFileTable.id == file_id)
        )
    assert status is not None
    return status


async def attach_screenshot_to_first_step(runs_container: RunsTestContainer, run_id: str, file_id: UUID) -> UUID:
    async with runs_container.database.begin():
        session = runs_container.database.get_current_session()
        case_result_id = await session.scalar(select(CaseResultTable.id).where(CaseResultTable.run_id == UUID(run_id)))
        assert case_result_id is not None
        await session.execute(
            update(StepResultTable)
            .where(StepResultTable.case_result_id == case_result_id, StepResultTable.step_order == 1)
            .values(screenshot_file_id=file_id)
        )
    return case_result_id


async def test_a_stale_claude_run_verifies_its_screenshots(
    client: AsyncClient, runs_container: RunsTestContainer, recording_mailer: RecordingMailer
) -> None:
    await runs_container.abort_stale_runs.execute(datetime.now(UTC))
    project = await seed_project(runs_container)
    runner = await sign_up_runner(client, runs_container, recording_mailer, project, ProjectRole.QC)
    story = await seed_runnable_story(runs_container, project, runner.account.user_id, case_count=1)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    steps: list[dict[str, object]] = [
        {"order": 1, "status": "passed", "actual_result": "Shown", "screenshot_path": "shots/1.png"},
        {"order": 2, "status": "passed", "actual_result": "Shown", "screenshot_path": "shots/2.png"},
    ]
    case_result_id = await record_case_id(client, runner.token, run_id, story.case_ids[0], "passed", steps)
    uploaded_key = f"projects/{project.id}/screenshot/{case_result_id}/1.png"
    runs_container.in_memory_object_storage.put(uploaded_key, b"png-bytes")
    await move_last_activity_back(runs_container, run_id, timedelta(hours=5))

    aborted_count = await runs_container.abort_stale_runs.execute(datetime.now(UTC))
    use_session(client, runner.account.session_token)
    run_response = await client.get(f"/api/projects/{project.key}/runs/{run_id}")

    assert aborted_count == 1
    assert await list_screenshot_files(runs_container, case_result_id) == [
        ("uploaded", uploaded_key),
        ("missing", f"projects/{project.id}/screenshot/{case_result_id}/2"),
    ]
    assert run_response.status_code == 200, run_response.text
    missing_screenshots = run_response.json()["report"]["missingScreenshots"]
    assert [(missing["caseResultId"], missing["stepOrder"]) for missing in missing_screenshots] == [(case_result_id, 2)]


async def test_a_manual_finish_runs_the_verifier_and_keeps_evidence(
    client: AsyncClient, runs_container: RunsTestContainer, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, runs_container, recording_mailer)
    evidence_file_id = await seed_evidence_file(runs_container, seeded.project.id, seeded.qc.user_id)
    run_id = await start_manual_run_id(client, seeded)
    record_response = await record_case(
        client,
        seeded.key,
        run_id,
        seeded.cases[0].id,
        steps=[build_step(1, "passed", evidenceFileId=str(evidence_file_id))],
    )
    assert record_response.status_code == 200, record_response.text

    finish_response = await finish_manual_run(client, seeded.key, run_id)
    run_response = await client.get(f"/api/projects/{seeded.key}/runs/{run_id}")

    assert finish_response.status_code == 200, finish_response.text
    assert await find_file_status(runs_container, evidence_file_id) is StoredFileStatus.UPLOADED
    assert run_response.json()["report"]["missingScreenshots"] == []


async def test_a_manual_finish_marks_an_unuploaded_screenshot_missing(
    client: AsyncClient, runs_container: RunsTestContainer, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, runs_container, recording_mailer)
    screenshot_file_id = await seed_evidence_file(
        runs_container, seeded.project.id, seeded.qc.user_id, StoredFileStatus.PENDING, StoredFileKind.SCREENSHOT
    )
    run_id = await start_manual_run_id(client, seeded)
    record_response = await record_case(client, seeded.key, run_id, seeded.cases[0].id, steps=[build_step(1, "passed")])
    assert record_response.status_code == 200, record_response.text
    case_result_id = await attach_screenshot_to_first_step(runs_container, run_id, screenshot_file_id)

    finish_response = await finish_manual_run(client, seeded.key, run_id)
    run_response = await client.get(f"/api/projects/{seeded.key}/runs/{run_id}")

    assert finish_response.status_code == 200, finish_response.text
    assert await find_file_status(runs_container, screenshot_file_id) is StoredFileStatus.MISSING
    missing_screenshots = run_response.json()["report"]["missingScreenshots"]
    assert [(missing["caseResultId"], missing["stepOrder"]) for missing in missing_screenshots] == [
        (str(case_result_id), 1)
    ]

from uuid import uuid4

import pytest
from httpx import AsyncClient, Response

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.runs.manual.manual_run_steps import (
    ManualRunProject,
    build_step,
    count_case_results,
    count_child_runs,
    find_run_row,
    finish_manual_run,
    record_case,
    record_case_status,
    rerun_failed_cases,
    seed_manual_run_project,
    sign_up_account,
    start_manual_run,
    start_manual_run_id,
)
from tests.api.test_data.project_steps import archive_project
from tests.conftest import RecordingMailer

ENDPOINTS = ["start", "record", "finish", "rerun"]


async def call_endpoint(client: AsyncClient, seeded: ManualRunProject, endpoint: str) -> Response:
    run_id = str(uuid4())
    if endpoint == "start":
        return await start_manual_run(client, seeded)
    if endpoint == "record":
        return await record_case(client, seeded.key, run_id, seeded.cases[0].id, status="passed")
    if endpoint == "finish":
        return await finish_manual_run(client, seeded.key, run_id)
    return await rerun_failed_cases(client, seeded.key, run_id)


@pytest.mark.parametrize("role", [ProjectRole.ADMIN, ProjectRole.QC])
async def test_admin_and_qc_run_the_whole_manual_flow(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    if role is not ProjectRole.QC:
        await sign_up_account(client, container, recording_mailer, seeded.project, role, "Runner")

    start_response = await start_manual_run(client, seeded)
    assert start_response.status_code == 201, start_response.text
    run_id = start_response.json()["id"]
    record_response = await record_case(client, seeded.key, run_id, seeded.cases[0].id, steps=[build_step(1, "failed")])
    assert record_response.status_code == 200, record_response.text
    finish_response = await finish_manual_run(client, seeded.key, run_id)
    assert finish_response.status_code == 200, finish_response.text
    rerun_response = await rerun_failed_cases(client, seeded.key, run_id)
    assert rerun_response.status_code == 201, rerun_response.text
    assert rerun_response.json()["parentRunId"] == run_id


@pytest.mark.parametrize("endpoint", ENDPOINTS)
@pytest.mark.parametrize("role", [ProjectRole.PM, ProjectRole.BA, ProjectRole.DEV, ProjectRole.VIEWER])
async def test_roles_without_manual_runs_are_denied(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole, endpoint: str
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    await sign_up_account(client, container, recording_mailer, seeded.project, role)

    response = await call_endpoint(client, seeded, endpoint)

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"


async def call_endpoint_on_run(client: AsyncClient, seeded: ManualRunProject, endpoint: str, run_id: str) -> Response:
    if endpoint == "record":
        return await record_case(client, seeded.key, run_id, seeded.cases[1].id, steps=[build_step(1, "failed")])
    if endpoint == "finish":
        return await finish_manual_run(client, seeded.key, run_id)
    return await rerun_failed_cases(client, seeded.key, run_id)


async def test_non_member_cannot_start_a_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    await sign_up_account(client, container, recording_mailer, seeded.project, None)

    response = await start_manual_run(client, seeded)

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


@pytest.mark.parametrize("endpoint", ["record", "finish", "rerun"])
async def test_non_member_gets_not_found_on_an_existing_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, endpoint: str
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    run_id = await start_manual_run_id(client, seeded)
    await record_case_status(client, seeded.key, run_id, seeded.cases[0].id, "failed")
    run_before = await find_run_row(container, run_id)
    await sign_up_account(client, container, recording_mailer, seeded.project, None)

    response = await call_endpoint_on_run(client, seeded, endpoint, run_id)

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"
    run_after = await find_run_row(container, run_id)
    assert (run_after.status, run_after.finished_at, run_after.last_activity_at, run_after.report) == (
        run_before.status,
        run_before.finished_at,
        run_before.last_activity_at,
        run_before.report,
    )
    assert await count_case_results(container, run_id) == 1
    assert await count_child_runs(container, run_id) == 0


@pytest.mark.parametrize("endpoint", ENDPOINTS)
async def test_archived_project_is_read_only(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, endpoint: str
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    await archive_project(container, seeded.project)

    response = await call_endpoint(client, seeded, endpoint)

    assert response.status_code == 409
    assert response.json()["code"] == "PROJECT_ARCHIVED"


async def test_signed_out_caller_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    client.cookies.clear()

    response = await start_manual_run(client, seeded)

    assert response.status_code == 401

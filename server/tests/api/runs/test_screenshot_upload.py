from uuid import uuid4

from httpx import AsyncClient, Response

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.runs.run_steps import (
    Runner,
    SeededRunnableStory,
    finish,
    record_case_id,
    seed_runnable_story,
    sign_up_runner,
    start_run_id,
)
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import read_tool_json


async def record_a_case(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[Runner, SeededRunnableStory, str, str]:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id, case_count=1)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    case_result_id = await record_case_id(client, runner.token, run_id, story.case_ids[0])
    return runner, story, run_id, case_result_id


async def request_screenshot_upload(
    client: AsyncClient, token: str | None, run_id: str, case_result_id: str
) -> Response:
    headers = {} if token is None else {"authorization": f"Bearer {token}"}
    return await client.post(f"/api/runs/{run_id}/case-results/{case_result_id}/screenshot-upload", headers=headers)


async def test_the_starter_gets_a_signed_upload_for_the_case_result(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id, case_result_id = await record_a_case(client, container, recording_mailer)

    response = await request_screenshot_upload(client, runner.token, run_id, case_result_id)

    assert response.status_code == 200
    assert response.json()["keyPrefix"] == f"projects/{story.project.id}/screenshot/{case_result_id}/"
    assert response.json().keys() == {"url", "fields", "keyPrefix"}


async def test_a_finished_run_still_signs_uploads(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, _, run_id, case_result_id = await record_a_case(client, container, recording_mailer)
    read_tool_json(await finish(client, runner.token, run_id))

    response = await request_screenshot_upload(client, runner.token, run_id, case_result_id)

    assert response.status_code == 200


async def test_another_member_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, story, run_id, case_result_id = await record_a_case(client, container, recording_mailer)
    other = await sign_up_runner(client, container, recording_mailer, story.project, ProjectRole.QC, "Other QC")

    response = await request_screenshot_upload(client, other.token, run_id, case_result_id)

    assert response.status_code == 403
    assert response.json()["code"] == "RUN_NOT_OWNED"


async def test_an_unknown_case_result_or_run_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, _, run_id, case_result_id = await record_a_case(client, container, recording_mailer)

    unknown_case_result = await request_screenshot_upload(client, runner.token, run_id, str(uuid4()))
    unknown_run = await request_screenshot_upload(client, runner.token, str(uuid4()), case_result_id)

    assert unknown_case_result.status_code == 404
    assert unknown_case_result.json()["code"] == "NOT_FOUND"
    assert unknown_run.status_code == 404


async def test_signed_upload_is_refused_without_a_bearer_token(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, _, run_id, case_result_id = await record_a_case(client, container, recording_mailer)

    response = await request_screenshot_upload(client, None, run_id, case_result_id)

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_API_TOKEN"


async def test_signed_upload_refuses_a_session_token(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, _, run_id, case_result_id = await record_a_case(client, container, recording_mailer)

    response = await request_screenshot_upload(client, runner.account.session_token, run_id, case_result_id)

    assert response.status_code == 401
    assert response.json()["code"] == "INVALID_API_TOKEN"


async def test_signed_upload_is_refused_for_a_viewer_token(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, story, run_id, case_result_id = await record_a_case(client, container, recording_mailer)
    viewer = await sign_up_runner(client, container, recording_mailer, story.project, ProjectRole.VIEWER, "Viewer")

    response = await request_screenshot_upload(client, viewer.token, run_id, case_result_id)

    assert response.status_code == 403
    assert response.json()["code"] == "PERMISSION_DENIED"

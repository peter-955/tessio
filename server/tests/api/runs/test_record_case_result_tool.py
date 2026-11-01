import json

import pytest
from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import create_token
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import (
    Runner,
    SeededRunnableStory,
    record_case,
    seed_runnable_story,
    sign_up_runner,
    start_run_id,
)
from tests.api.test_data.project_steps import add_member, archive_project, seed_project
from tests.conftest import RecordingMailer


async def start_a_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole = ProjectRole.QC
) -> tuple[Runner, SeededRunnableStory, str]:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project, role)
    story = await seed_runnable_story(container, project, runner.account.user_id)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    return runner, story, run_id


def read_error_text(response_json: dict[str, dict[str, object]]) -> str:
    result = response_json["result"]
    assert result["isError"] is True
    content = result["content"]
    assert isinstance(content, list)
    text: str = content[0]["text"]
    return text


@pytest.mark.parametrize("role", [ProjectRole.QC, ProjectRole.DEV, ProjectRole.ADMIN])
async def test_tool_result_holds_only_the_case_result_id(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer, role)

    response = await record_case(client, runner.token, run_id, story.case_ids[0])

    result = response.json()["result"]
    assert result.get("isError") is not True
    assert result.get("structuredContent") is None
    assert json.loads(result["content"][0]["text"]).keys() == {"case_result_id"}


@pytest.mark.parametrize("role", [ProjectRole.PM, ProjectRole.BA, ProjectRole.VIEWER])
async def test_tool_is_refused_for_roles_that_cannot_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer)
    other = await sign_up_runner(client, container, recording_mailer, story.project, role, "Other Member")

    response = await record_case(client, other.token, run_id, story.case_ids[0])

    assert read_error_text(response.json()).startswith("PERMISSION_DENIED: ")
    assert runner.token != other.token


async def test_tool_is_refused_without_a_token(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, story, run_id = await start_a_run(client, container, recording_mailer)

    response = await record_case(client, "", run_id, story.case_ids[0])

    assert read_error_text(response.json()) == "INVALID_API_TOKEN: The API token is invalid, expired or revoked."


async def test_tool_refuses_a_session_token(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer)

    response = await record_case(client, runner.account.session_token, run_id, story.case_ids[0])

    assert read_error_text(response.json()).startswith("INVALID_API_TOKEN: ")


async def test_tool_is_refused_on_an_archived_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer)
    await archive_project(container, story.project)

    response = await record_case(client, runner.token, run_id, story.case_ids[0])

    assert read_error_text(response.json()).startswith("PROJECT_ARCHIVED: ")


async def test_tool_refuses_a_token_of_another_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story, run_id = await start_a_run(client, container, recording_mailer)
    other_project = await seed_project(container)
    await add_member(container, other_project, runner.account.user_id, ProjectRole.QC)
    use_session(client, runner.account.session_token)
    other_token = await create_token(client, other_project.key)
    client.cookies.clear()

    response = await record_case(client, other_token, run_id, story.case_ids[0])

    assert read_error_text(response.json()) == "NOT_FOUND: Run not found."

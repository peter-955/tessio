from uuid import uuid4

from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import create_token
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import (
    finish,
    read_tool_error_code,
    record_case_id,
    seed_runnable_story,
    sign_up_runner,
    start_run_id,
)
from tests.api.test_data.project_steps import add_member, archive_project, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json


async def test_failed_cases_lists_failed_and_blocked_results_in_run_order(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id, case_count=4)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    await record_case_id(client, runner.token, run_id, story.case_ids[2], "failed")
    await record_case_id(client, runner.token, run_id, story.case_ids[0], "blocked")
    await record_case_id(client, runner.token, run_id, story.case_ids[1], "passed")

    running = read_tool_json(await call_tool(client, runner.token, "get_failed_cases", {"run_id": run_id}))
    read_tool_json(await finish(client, runner.token, run_id))
    finished = read_tool_json(await call_tool(client, runner.token, "get_failed_cases", {"run_id": run_id}))

    assert running["run_status"] == "running"
    assert finished.keys() == {"run_id", "run_status", "story_key", "environment", "cases"}
    assert finished["run_id"] == run_id
    assert finished["run_status"] == "failed"
    assert finished["story_key"] == story.jira_key
    assert finished["environment"] == "Staging"
    cases = finished["cases"]
    assert isinstance(cases, list)
    assert [(case["case_id"], case["status"]) for case in cases] == [
        (str(story.case_ids[0]), "blocked"),
        (str(story.case_ids[2]), "failed"),
    ]
    assert cases[0].keys() == {"case_id", "code", "title", "status"}


async def test_viewers_can_read_failed_cases_even_on_an_archived_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    viewer = await sign_up_runner(client, container, recording_mailer, project, ProjectRole.VIEWER, "Viewer")
    story = await seed_runnable_story(container, project, runner.account.user_id)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    await archive_project(container, project)

    content = read_tool_json(await call_tool(client, viewer.token, "get_failed_cases", {"run_id": run_id}))

    assert content["cases"] == []


async def test_failed_cases_of_another_project_are_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    other_project = await seed_project(container)
    await add_member(container, other_project, runner.account.user_id, ProjectRole.QC)
    use_session(client, runner.account.session_token)
    other_token = await create_token(client, other_project.key)
    client.cookies.clear()

    foreign = await call_tool(client, other_token, "get_failed_cases", {"run_id": run_id})
    unknown = await call_tool(client, runner.token, "get_failed_cases", {"run_id": str(uuid4())})

    assert read_tool_error_code(foreign) == "NOT_FOUND"
    assert read_tool_error_code(unknown) == "NOT_FOUND"

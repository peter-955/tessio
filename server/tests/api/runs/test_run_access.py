from dataclasses import dataclass

import pytest
from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.api_tokens.api_token_steps import create_token
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import (
    Runner,
    SeededRunnableStory,
    read_tool_error_code,
    record_case_id,
    seed_runnable_story,
    sign_up_runner,
    start_run_id,
)
from tests.api.test_data.project_steps import add_member, archive_project, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool


@dataclass(frozen=True)
class RecordedRun:
    runner: Runner
    story: SeededRunnableStory
    run_id: str
    case_result_id: str


async def record_a_run(client: AsyncClient, container: Container, recording_mailer: RecordingMailer) -> RecordedRun:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    case_result_id = await record_case_id(client, runner.token, run_id, story.case_ids[0])
    return RecordedRun(runner=runner, story=story, run_id=run_id, case_result_id=case_result_id)


def build_tool_arguments(tool_name: str, recorded_run: RecordedRun) -> dict[str, object]:
    if tool_name == "start_run":
        return {"story_key": recorded_run.story.jira_key}
    if tool_name == "record_case_result":
        return {
            "run_id": recorded_run.run_id,
            "case_id": str(recorded_run.story.case_ids[1]),
            "status": "passed",
            "duration_ms": 10,
            "steps": [{"order": 1, "status": "passed", "actual_result": "Shown"}],
        }
    return {"run_id": recorded_run.run_id}


async def create_token_for_another_project(client: AsyncClient, container: Container, runner: Runner) -> str:
    other_project = await seed_project(container)
    await add_member(container, other_project, runner.account.user_id, ProjectRole.QC)
    use_session(client, runner.account.session_token)
    token = await create_token(client, other_project.key)
    client.cookies.clear()
    return token


@pytest.mark.parametrize(
    ("tool_name", "expected_code"),
    [
        ("start_run", "PROJECT_ARCHIVED"),
        ("record_case_result", "PROJECT_ARCHIVED"),
        ("finish_run", "PROJECT_ARCHIVED"),
    ],
)
async def test_writing_tools_are_refused_on_an_archived_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, tool_name: str, expected_code: str
) -> None:
    recorded_run = await record_a_run(client, container, recording_mailer)
    await archive_project(container, recorded_run.story.project)

    response = await call_tool(
        client, recorded_run.runner.token, tool_name, build_tool_arguments(tool_name, recorded_run)
    )

    assert read_tool_error_code(response) == expected_code


@pytest.mark.parametrize("tool_name", ["start_run", "record_case_result", "finish_run", "get_failed_cases"])
async def test_tools_never_reach_another_projects_runs(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, tool_name: str
) -> None:
    recorded_run = await record_a_run(client, container, recording_mailer)
    other_token = await create_token_for_another_project(client, container, recorded_run.runner)

    response = await call_tool(client, other_token, tool_name, build_tool_arguments(tool_name, recorded_run))

    assert read_tool_error_code(response) == "NOT_FOUND"


async def test_screenshot_upload_is_refused_on_archived_and_other_projects(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    recorded_run = await record_a_run(client, container, recording_mailer)
    other_token = await create_token_for_another_project(client, container, recorded_run.runner)
    path = f"/api/runs/{recorded_run.run_id}/case-results/{recorded_run.case_result_id}/screenshot-upload"

    other_project = await client.post(path, headers={"authorization": f"Bearer {other_token}"})
    await archive_project(container, recorded_run.story.project)
    archived = await client.post(path, headers={"authorization": f"Bearer {recorded_run.runner.token}"})

    assert other_project.status_code == 404
    assert archived.status_code == 409
    assert archived.json()["code"] == "PROJECT_ARCHIVED"


async def test_run_reads_stay_open_on_an_archived_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    recorded_run = await record_a_run(client, container, recording_mailer)
    await archive_project(container, recorded_run.story.project)
    use_session(client, recorded_run.runner.account.session_token)
    project_key = recorded_run.story.project.key

    listed = await client.get(f"/api/projects/{project_key}/runs")
    detail = await client.get(f"/api/projects/{project_key}/runs/{recorded_run.run_id}")

    assert listed.status_code == 200
    assert detail.status_code == 200

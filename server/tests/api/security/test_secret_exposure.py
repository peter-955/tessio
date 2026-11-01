import logging

import pytest
from httpx import AsyncClient

from app.container import Container
from app.shared.masking import MASKED_VALUE
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import (
    finish,
    record_case,
    seed_runnable_story,
    seed_secret,
    sign_up_runner,
    start_run_id,
)
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool

SECRET_VALUE = "S3cr3t-Value-42"


async def test_a_secret_used_in_a_run_never_appears_in_any_response_or_log(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, caplog: pytest.LogCaptureFixture
) -> None:
    caplog.set_level(logging.DEBUG)
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project, ProjectRole.QC)
    story = await seed_runnable_story(container, project, runner.account.user_id, case_count=1, step_count=1)
    await seed_secret(container, project, "ADMIN_PASSWORD", SECRET_VALUE)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    record_response = await record_case(
        client,
        runner.token,
        run_id,
        story.case_ids[0],
        "failed",
        [
            {
                "order": 1,
                "status": "failed",
                "actual_result": f"Typed {SECRET_VALUE} into the form",
                "error": f"Login refused for {SECRET_VALUE}",
            }
        ],
    )
    finish_response = await finish(client, runner.token, run_id, f"Password {SECRET_VALUE} was rejected")
    failure_id = read_failure_id(await list_failures(client, runner.account.session_token, project.key))

    responses = [
        record_response,
        finish_response,
        await client.get(f"/api/projects/{project.key}/runs"),
        await client.get(f"/api/projects/{project.key}/runs/{run_id}"),
        await client.get(f"/api/projects/{project.key}/failures"),
        await client.get(f"/api/projects/{project.key}/failures/{failure_id}"),
        await client.get(f"/api/projects/{project.key}/stories/{story.jira_key}/traceability"),
        await client.get(f"/api/projects/{project.key}/case-latest-results"),
        await client.get(f"/api/projects/{project.key}/story-progress"),
        await client.get(f"/api/projects/{project.key}/dashboard"),
        await client.get(f"/api/projects/{project.key}/my-work"),
        await client.get(f"/api/projects/{project.key}/test-data"),
        await client.get(f"/api/projects/{project.key}/test-data/effective"),
        await client.get("/api/notifications"),
        await call_tool(client, runner.token, "get_story_context", {"story_key": story.jira_key}),
        await call_tool(client, runner.token, "get_failed_cases", {"run_id": run_id}),
    ]

    assert [response.status_code for response in responses] == [200] * len(responses)
    assert [response.request.url.path for response in responses if SECRET_VALUE in response.text] == []
    assert SECRET_VALUE not in caplog.text
    assert MASKED_VALUE in responses[3].text


async def list_failures(client: AsyncClient, session_token: str, project_key: str) -> list[dict[str, object]]:
    use_session(client, session_token)
    response = await client.get(f"/api/projects/{project_key}/failures")
    assert response.status_code == 200, response.text
    failures: list[dict[str, object]] = response.json()
    return failures


def read_failure_id(failures: list[dict[str, object]]) -> str:
    assert len(failures) == 1
    failure_id = failures[0]["id"]
    assert isinstance(failure_id, str)
    return failure_id

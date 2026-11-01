from uuid import uuid4

from httpx import AsyncClient

from app.container import Container
from app.modules.users import WorkspaceRole
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import sign_up_as, use_session
from tests.api.runs.run_steps import (
    Runner,
    SeededRunnableStory,
    finish,
    record_case_id,
    seed_runnable_story,
    sign_up_runner,
    start_run_id,
)
from tests.api.runs.runs_test_container import RunsTestContainer
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import read_tool_json


async def seed_finished_and_running_runs(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> tuple[Runner, SeededRunnableStory, SeededRunnableStory, str, str]:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project, name="Quinn Runner")
    first_story = await seed_runnable_story(container, project, runner.account.user_id, case_count=2)
    second_story = await seed_runnable_story(container, project, runner.account.user_id, case_count=1)
    finished_run_id = await start_run_id(client, runner.token, first_story.jira_key)
    await record_case_id(client, runner.token, finished_run_id, first_story.case_ids[0], "failed")
    read_tool_json(await finish(client, runner.token, finished_run_id, "One failure"))
    running_run_id = await start_run_id(client, runner.token, second_story.jira_key)
    return runner, first_story, second_story, finished_run_id, running_run_id


async def test_run_list_is_newest_first_and_filters(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, first_story, _, finished_run_id, running_run_id = await seed_finished_and_running_runs(
        client, container, recording_mailer
    )
    use_session(client, runner.account.session_token)
    project_key = first_story.project.key

    listed = await client.get(f"/api/projects/{project_key}/runs")
    by_story = await client.get(f"/api/projects/{project_key}/runs", params={"storyKey": first_story.jira_key})
    by_status = await client.get(f"/api/projects/{project_key}/runs", params={"status": "running"})
    limited = await client.get(f"/api/projects/{project_key}/runs", params={"limit": 1})
    too_many = await client.get(f"/api/projects/{project_key}/runs", params={"limit": 201})
    unknown_story = await client.get(f"/api/projects/{project_key}/runs", params={"storyKey": "NOPE-1"})

    assert listed.status_code == 200
    assert [run["id"] for run in listed.json()] == [running_run_id, finished_run_id]
    finished = listed.json()[1]
    assert finished["storyJiraKey"] == first_story.jira_key
    assert finished["storyTitle"] == f"Story {first_story.jira_key}"
    assert finished["environmentName"] == "Staging"
    assert finished["executor"] == "claude"
    assert finished["status"] == "failed"
    assert finished["abortReason"] is None
    assert finished["startedBy"] == str(runner.account.user_id)
    assert finished["startedByName"] == "Quinn Runner"
    assert finished["finishedAt"] is not None
    assert finished["counts"] == {
        "total": 2,
        "passed": 0,
        "failed": 1,
        "blocked": 0,
        "skipped": 0,
        "notReported": 1,
    }
    assert [run["id"] for run in by_story.json()] == [finished_run_id]
    assert [run["id"] for run in by_status.json()] == [running_run_id]
    assert [run["id"] for run in limited.json()] == [running_run_id]
    assert too_many.status_code == 422
    assert unknown_story.status_code == 404


async def test_run_detail_shows_steps_screenshots_report_and_child_runs(
    client: AsyncClient, runs_container: RunsTestContainer, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(runs_container)
    runner = await sign_up_runner(client, runs_container, recording_mailer, project)
    story = await seed_runnable_story(runs_container, project, runner.account.user_id, case_count=2, step_count=2)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    steps: list[dict[str, object]] = [
        {"order": 1, "status": "passed", "actual_result": "Opened", "screenshot_path": "shots/1.png"},
        {"order": 2, "status": "failed", "actual_result": "Broken", "error": "Boom", "screenshot_path": "s/2.png"},
    ]
    case_result_id = await record_case_id(client, runner.token, run_id, story.case_ids[0], "failed", steps)
    runs_container.in_memory_object_storage.put(f"projects/{project.id}/screenshot/{case_result_id}/1.png", b"png")
    read_tool_json(await finish(client, runner.token, run_id, "Checkout broke"))
    child_run_id = await start_run_id(client, runner.token, story.jira_key, parent_run_id=run_id)
    use_session(client, runner.account.session_token)

    response = await client.get(f"/api/projects/{project.key}/runs/{run_id}")

    assert response.status_code == 200
    detail = response.json()
    assert detail["id"] == run_id
    assert detail["summary"] == "Checkout broke"
    assert detail["childRunIds"] == [child_run_id]
    assert detail["counts"]["failed"] == 1
    assert detail["counts"]["notReported"] == 1
    assert detail["report"]["counts"]["total"] == 2
    assert detail["report"]["summary"] == "Checkout broke"
    assert detail["report"]["failedCases"][0]["stepOrder"] == 2
    assert detail["report"]["missingScreenshots"][0]["stepOrder"] == 2
    first_case, second_case = detail["cases"]
    assert first_case["testCaseId"] == str(story.case_ids[0])
    assert first_case["code"].startswith("TC-")
    assert first_case["versionNumber"] == 1
    assert first_case["position"] == 1
    assert first_case["result"]["id"] == case_result_id
    assert first_case["result"]["status"] == "failed"
    assert first_case["result"]["durationMs"] == 900
    assert [
        (step["order"], step["action"], step["status"], step["actualResult"], step["error"], step["screenshotStatus"])
        for step in first_case["steps"]
    ] == [
        (1, "Action 1", "passed", "Opened", None, "uploaded"),
        (2, "Action 2", "failed", "Broken", "Boom", "missing"),
    ]
    assert first_case["steps"][0]["screenshotFileId"] is not None
    assert first_case["steps"][0]["expected"] == "Expected 1"
    assert second_case["result"] is None
    assert [step["status"] for step in second_case["steps"]] == [None, None]


async def test_run_reads_need_membership(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, story, _, finished_run_id, _ = await seed_finished_and_running_runs(client, container, recording_mailer)
    project_key = story.project.key
    viewer = await sign_up_runner(client, container, recording_mailer, story.project, ProjectRole.VIEWER, "Viewer")
    outsider = await sign_up_as(client, container, recording_mailer, WorkspaceRole.MEMBER, "Outsider")

    use_session(client, outsider.session_token)
    outsider_list = await client.get(f"/api/projects/{project_key}/runs")
    outsider_detail = await client.get(f"/api/projects/{project_key}/runs/{finished_run_id}")
    use_session(client, viewer.account.session_token)
    viewer_list = await client.get(f"/api/projects/{project_key}/runs")
    viewer_detail = await client.get(f"/api/projects/{project_key}/runs/{finished_run_id}")
    unknown_detail = await client.get(f"/api/projects/{project_key}/runs/{uuid4()}")

    assert outsider_list.status_code == 404
    assert outsider_detail.status_code == 404
    assert viewer_list.status_code == 200
    assert viewer_detail.status_code == 200
    assert unknown_detail.status_code == 404
    assert unknown_detail.json()["code"] == "NOT_FOUND"


async def test_run_detail_of_another_project_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, _, _, finished_run_id, _ = await seed_finished_and_running_runs(client, container, recording_mailer)
    other_project = await seed_project(container)
    other_member = await sign_up_runner(client, container, recording_mailer, other_project, ProjectRole.QC, "Other")
    assert runner.token != other_member.token
    use_session(client, other_member.account.session_token)

    response = await client.get(f"/api/projects/{other_project.key}/runs/{finished_run_id}")

    assert response.status_code == 404

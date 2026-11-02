from httpx import AsyncClient

from app.container import Container
from app.shared.permissions import ProjectRole
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import read_tool_error_code, seed_secret, sign_up_runner
from tests.api.suites.suite_steps import (
    DEFAULT_SUITE_NAME,
    archive_suite,
    create_suite_id,
    find_case_code,
    flag_needs_review,
    link_criterion,
    seed_suite,
    seed_suite_world,
    set_case_data_keys,
    start_suite_run,
)
from tests.api.test_data.project_steps import add_member, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json


async def get_suite_context(client: AsyncClient, token: str, suite: str) -> dict[str, object]:
    return read_tool_json(await call_tool(client, token, "get_suite_context", {"suite": suite}))


async def test_suite_context_groups_the_ready_cases_by_story_in_suite_order(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await link_criterion(container, world.second_story.story_id, world.second_story.case_ids[:1])
    await flag_needs_review(container, world.case_ids[1])
    await seed_secret(container, world.project, "ADMIN_PASSWORD", "s3cr3t-Value")
    await set_case_data_keys(container, world.case_ids[3], ["ADMIN_PASSWORD"])
    suite_id = await seed_suite(
        client, world, case_ids=[world.case_ids[3], world.case_ids[0], world.case_ids[2], world.case_ids[1]]
    )

    content = await get_suite_context(client, world.runner.token, DEFAULT_SUITE_NAME.lower())

    assert content["suite"] == {"id": suite_id, "name": DEFAULT_SUITE_NAME}
    assert content["case_count"] == 3
    stories = content["stories"]
    assert isinstance(stories, list)
    assert [story["key"] for story in stories] == [world.second_story.jira_key, world.first_story.jira_key]
    assert [case["id"] for case in stories[0]["cases"]] == [str(world.case_ids[3]), str(world.case_ids[2])]
    assert [case["id"] for case in stories[1]["cases"]] == [str(world.case_ids[0])]
    assert stories[0]["criteria"] == [{"code": "AC-1", "text": "Criterion AC-1"}]
    assert stories[0]["cases"][1]["criteria"] == ["AC-1"]
    assert stories[0]["test_status"] == "not_started"
    first_case = stories[0]["cases"][0]
    assert first_case["steps"][0] == {"order": 1, "action": "Action 1", "expected": "Expected 1"}
    assert first_case["data_keys"] == ["ADMIN_PASSWORD"]
    assert content["skipped_cases"] == [
        {
            "code": await find_case_code(container, world.case_ids[1]),
            "title": "Case " + (await find_case_code(container, world.case_ids[1])).removeprefix("TC-"),
            "story_key": world.first_story.jira_key,
            "reason": "needs_review",
        }
    ]
    assert content["data"] == [{"key": "ADMIN_PASSWORD", "kind": "secret", "value": "{{data.ADMIN_PASSWORD}}"}]
    assert "s3cr3t-Value" not in str(content)
    environments = content["environments"]
    assert isinstance(environments, list)
    assert [environment["name"] for environment in environments] == ["Staging"]


async def test_suite_context_takes_the_suite_id(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)

    content = await get_suite_context(client, world.runner.token, suite_id)

    assert content["case_count"] == 4


async def test_suite_context_refuses_unknown_archived_and_foreign_suites(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    other_project = await seed_project(container)
    await add_member(container, other_project, world.runner.account.user_id, ProjectRole.QC)
    foreign_suite_id = await create_suite_id(client, other_project.key, "Foreign")
    assert (await archive_suite(client, world.key, suite_id)).status_code == 200

    unknown = await call_tool(client, world.runner.token, "get_suite_context", {"suite": "Nightly"})
    archived = await call_tool(client, world.runner.token, "get_suite_context", {"suite": suite_id})
    foreign = await call_tool(client, world.runner.token, "get_suite_context", {"suite": foreign_suite_id})
    foreign_run = await start_suite_run(client, world.runner.token, foreign_suite_id)

    assert read_tool_error_code(unknown) == "NOT_FOUND"
    assert read_tool_error_code(archived) == "SUITE_ARCHIVED"
    assert read_tool_error_code(foreign) == "NOT_FOUND"
    assert read_tool_error_code(foreign_run) == "NOT_FOUND"


async def test_a_viewer_reads_the_suite_context_but_cannot_start_a_suite_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await seed_suite(client, world)
    viewer = await sign_up_runner(client, container, recording_mailer, world.project, ProjectRole.VIEWER, "Vic Viewer")
    use_session(client, world.runner.account.session_token)

    content = await get_suite_context(client, viewer.token, DEFAULT_SUITE_NAME)
    started = await start_suite_run(client, viewer.token, DEFAULT_SUITE_NAME)

    assert content["case_count"] == 4
    assert read_tool_error_code(started) == "PERMISSION_DENIED"

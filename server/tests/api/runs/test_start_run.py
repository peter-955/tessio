from uuid import UUID

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from app.container import Container
from app.modules.runs.infrastructure import RunCaseTable, RunTable
from app.modules.stories.infrastructure import StoryTable
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import SeededStory, raise_gap_id
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import (
    Runner,
    SeededRunnableStory,
    change_case_status,
    edit_case,
    finish,
    read_tool_error,
    read_tool_error_code,
    record_case,
    seed_environment,
    seed_runnable_story,
    sign_up_runner,
    start_run_for,
    start_run_id,
)
from tests.api.test_data.project_steps import archive_project, seed_project
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import read_tool_json
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def seed_runner_story(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    role: ProjectRole = ProjectRole.QC,
    case_count: int = 2,
    step_count: int = 2,
) -> tuple[Runner, SeededRunnableStory]:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project, role)
    story = await seed_runnable_story(container, project, runner.account.user_id, case_count, step_count)
    return runner, story


async def test_start_run_replies_with_the_environment_and_the_fixed_cases(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer, step_count=3)

    content = read_tool_json(await start_run_for(client, runner.token, story.jira_key.lower()))

    assert content.keys() == {"run_id", "environment", "base_url", "health_check_url", "cases"}
    assert content["environment"] == "Staging"
    assert content["base_url"] == "https://staging.shop.test"
    assert content["health_check_url"] == "https://staging.shop.test/health"
    cases = content["cases"]
    assert isinstance(cases, list)
    assert [case["case_id"] for case in cases] == [str(case_id) for case_id in story.case_ids]
    first_case = cases[0]
    assert first_case.keys() == {"case_id", "code", "title", "version", "preconditions", "steps"}
    assert first_case["code"].startswith("TC-")
    assert first_case["version"] == 1
    assert first_case["preconditions"] == "Signed out"
    assert first_case["steps"] == [
        {"order": order, "action": f"Action {order}", "expected": f"Expected {order}"} for order in (1, 2, 3)
    ]


async def test_start_run_moves_the_story_in_test_and_publishes_events(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    recording_live_event_publisher.events.clear()

    run_id = await start_run_id(client, runner.token, story.jira_key)

    async with container.database.begin():
        session = container.database.get_current_session()
        story_row = await session.scalar(select(StoryTable).where(StoryTable.id == story.story_id))
        run_row = await session.scalar(select(RunTable).where(RunTable.id == UUID(run_id)))
    assert story_row is not None
    assert story_row.test_status == "in_test"
    assert run_row is not None
    assert run_row.executor == "claude"
    assert run_row.status == "running"
    assert run_row.started_by == runner.account.user_id
    assert run_row.started_via_token_id is not None
    assert run_row.environment_id == story.environment_id
    events = {event.type: event.ids for event in recording_live_event_publisher.events}
    assert events[LiveEventType.RUN_STARTED] == {"runId": run_id, "storyId": str(story.story_id)}
    assert events[LiveEventType.STORY_CHANGED] == {"storyId": str(story.story_id), "jiraKey": story.jira_key}


async def test_run_cases_keep_the_version_after_a_later_edit(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer, case_count=1)
    run_id = await start_run_id(client, runner.token, story.jira_key)
    async with container.database.begin():
        first_version_id = await container.database.get_current_session().scalar(
            select(RunCaseTable.test_case_version_id).where(RunCaseTable.run_id == UUID(run_id))
        )

    await edit_case(container, story.case_ids[0], "Edited title", 4, runner.account.user_id)

    async with container.database.begin():
        kept_version_id = await container.database.get_current_session().scalar(
            select(RunCaseTable.test_case_version_id).where(RunCaseTable.run_id == UUID(run_id))
        )
    assert kept_version_id == first_version_id
    recorded = read_tool_json(await record_case(client, runner.token, run_id, story.case_ids[0], "passed"))
    assert recorded.keys() == {"case_result_id"}


async def test_start_run_is_blocked_by_open_gaps(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    use_session(client, runner.account.session_token)
    await raise_gap_id(
        client, story.project.key, SeededStory(id=story.story_id, jira_key=story.jira_key, criterion_ids={})
    )
    client.cookies.clear()

    response = await start_run_for(client, runner.token, story.jira_key)

    assert read_tool_error_code(response) == "OPEN_GAPS_BLOCK_RUN"


async def test_start_run_needs_ready_cases(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    project = await seed_project(container)
    runner = await sign_up_runner(client, container, recording_mailer, project)
    story = await seed_runnable_story(container, project, runner.account.user_id, status="draft")

    response = await start_run_for(client, runner.token, story.jira_key)

    assert read_tool_error_code(response) == "NO_READY_CASES"


async def test_start_run_refuses_a_draft_case_and_a_foreign_case(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    await change_case_status(container, story.case_ids[1], "draft")
    other_story = await seed_runnable_story(container, story.project, runner.account.user_id, case_count=1)

    draft_response = await start_run_for(client, runner.token, story.jira_key, case_ids=[str(story.case_ids[1])])
    foreign_response = await start_run_for(
        client, runner.token, story.jira_key, case_ids=[str(other_story.case_ids[0])]
    )

    assert read_tool_error(draft_response).startswith("CASE_NOT_READY: TC-")
    assert read_tool_error_code(foreign_response) == "UNKNOWN_REFERENCE"


async def test_start_run_keeps_the_picked_order_without_duplicates(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer, case_count=3)
    picked = [story.case_ids[2], story.case_ids[0], story.case_ids[2]]

    content = read_tool_json(
        await start_run_for(client, runner.token, story.jira_key, case_ids=[str(case_id) for case_id in picked])
    )

    cases = content["cases"]
    assert isinstance(cases, list)
    assert [case["case_id"] for case in cases] == [str(story.case_ids[2]), str(story.case_ids[0])]


async def test_second_start_on_the_same_story_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    await start_run_id(client, runner.token, story.jira_key)

    response = await start_run_for(client, runner.token, story.jira_key)

    assert read_tool_error_code(response) == "RUN_ALREADY_RUNNING"


async def test_unknown_story_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, _ = await seed_runner_story(client, container, recording_mailer)

    response = await start_run_for(client, runner.token, "NOPE-1")

    assert read_tool_error_code(response) == "NOT_FOUND"


async def test_environment_name_matches_without_case(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    await seed_environment(container, story.project, "Production")

    content = read_tool_json(await start_run_for(client, runner.token, story.jira_key, environment=" production "))

    assert content["environment"] == "Production"


async def test_environment_falls_back_to_the_project_default(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    await seed_environment(container, story.project, "Production", is_default=True)

    content = read_tool_json(await start_run_for(client, runner.token, story.jira_key))

    assert content["environment"] == "Production"


async def test_environment_falls_back_to_the_only_active_one(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    await seed_environment(container, story.project, "Legacy", is_archived=True, is_default=True)

    content = read_tool_json(await start_run_for(client, runner.token, story.jira_key))

    assert content["environment"] == "Staging"


async def test_environment_is_required_when_several_are_active(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    await seed_environment(container, story.project, "Production")

    response = await start_run_for(client, runner.token, story.jira_key)

    assert read_tool_error(response) == "INVALID_REQUEST: Pick an environment: Production, Staging."


async def test_unknown_or_archived_environment_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    await seed_environment(container, story.project, "Legacy", is_archived=True)

    unknown = await start_run_for(client, runner.token, story.jira_key, environment="Nowhere")
    archived = await start_run_for(client, runner.token, story.jira_key, environment="Legacy")

    assert read_tool_error_code(unknown) == "UNKNOWN_REFERENCE"
    assert read_tool_error_code(archived) == "UNKNOWN_REFERENCE"


async def finish_with_results(
    client: AsyncClient, runner: Runner, story: SeededRunnableStory, statuses: list[str]
) -> str:
    run_id = await start_run_id(client, runner.token, story.jira_key)
    for case_id, status in zip(story.case_ids, statuses, strict=False):
        read_tool_json(await record_case(client, runner.token, run_id, case_id, status))
    read_tool_json(await finish(client, runner.token, run_id))
    return run_id


async def test_rerun_takes_the_failed_and_blocked_cases_that_are_still_ready(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer, case_count=4)
    parent_run_id = await finish_with_results(client, runner, story, ["failed", "passed", "blocked", "failed"])
    await change_case_status(container, story.case_ids[3], "draft")

    content = read_tool_json(await start_run_for(client, runner.token, story.jira_key, parent_run_id=parent_run_id))

    cases = content["cases"]
    assert isinstance(cases, list)
    assert [case["case_id"] for case in cases] == [str(story.case_ids[0]), str(story.case_ids[2])]
    async with container.database.begin():
        run_row = await container.database.get_current_session().scalar(
            select(RunTable).where(RunTable.id == UUID(str(content["run_id"])))
        )
    assert run_row is not None
    assert str(run_row.parent_run_id) == parent_run_id


async def test_rerun_without_failed_cases_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    parent_run_id = await finish_with_results(client, runner, story, ["passed", "skipped"])

    response = await start_run_for(client, runner.token, story.jira_key, parent_run_id=parent_run_id)

    assert read_tool_error_code(response) == "NO_FAILED_CASES_TO_RERUN"


async def test_rerun_of_a_running_parent_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    parent_run_id = await start_run_id(client, runner.token, story.jira_key)

    response = await start_run_for(client, runner.token, story.jira_key, parent_run_id=parent_run_id)

    assert read_tool_error_code(response) == "RUN_NOT_FINISHED"


async def test_rerun_of_another_story_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    parent_run_id = await finish_with_results(client, runner, story, ["failed", "failed"])
    other_story = await seed_runnable_story(container, story.project, runner.account.user_id)

    response = await start_run_for(client, runner.token, other_story.jira_key, parent_run_id=parent_run_id)

    assert read_tool_error(response) == "INVALID_REQUEST: The parent run belongs to another story."


async def test_rerun_with_case_ids_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    parent_run_id = await finish_with_results(client, runner, story, ["failed", "failed"])

    response = await start_run_for(
        client, runner.token, story.jira_key, parent_run_id=parent_run_id, case_ids=[str(story.case_ids[0])]
    )

    assert read_tool_error_code(response) == "INVALID_REQUEST"


@pytest.mark.parametrize("role", [ProjectRole.QC, ProjectRole.DEV, ProjectRole.ADMIN])
async def test_runner_roles_can_start(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer, role)

    content = read_tool_json(await start_run_for(client, runner.token, story.jira_key))

    assert "run_id" in content


@pytest.mark.parametrize("role", [ProjectRole.PM, ProjectRole.BA, ProjectRole.VIEWER])
async def test_other_roles_cannot_start(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, role: ProjectRole
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer, role)

    response = await start_run_for(client, runner.token, story.jira_key)

    assert read_tool_error_code(response) == "PERMISSION_DENIED"


async def test_start_is_refused_on_an_archived_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    runner, story = await seed_runner_story(client, container, recording_mailer)
    await archive_project(container, story.project)

    response = await start_run_for(client, runner.token, story.jira_key)

    assert read_tool_error_code(response) == "PROJECT_ARCHIVED"

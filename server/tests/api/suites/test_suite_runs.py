import asyncio
from datetime import UTC, datetime
from uuid import UUID, uuid7

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.container import Container
from app.modules.notifications.infrastructure import NotificationTable
from app.modules.runs import Run, RunExecutor, RunStatus
from app.modules.runs.errors import SuiteAlreadyRunningError
from app.modules.runs.infrastructure import RunTable
from app.modules.stories import TestStatus as StoryTestStatus
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.gaps.gap_steps import add_active_member
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import (
    change_case_status,
    finish,
    read_tool_error,
    read_tool_error_code,
    sign_up_runner,
    start_run_for,
)
from tests.api.suites.suite_steps import (
    DEFAULT_SUITE_NAME,
    SuiteWorld,
    archive_suite,
    find_case_code,
    find_story_test_status,
    flag_needs_review,
    put_story_test_status,
    raise_story_gap,
    record_suite_case,
    seed_suite,
    seed_suite_world,
    set_story_test_status,
    start_manual_suite_run,
    start_suite_run,
    start_suite_run_content,
)
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import call_tool, read_tool_json
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


def build_running_suite_run(world: SuiteWorld, suite_id: str) -> Run:
    now = datetime.now(UTC)
    return Run(
        id=uuid7(),
        project_id=world.project.id,
        story_id=None,
        environment_id=world.first_story.environment_id,
        executor=RunExecutor.MANUAL,
        status=RunStatus.RUNNING,
        abort_reason=None,
        parent_run_id=None,
        started_by=world.runner.account.user_id,
        started_via_token_id=None,
        summary=None,
        report=None,
        started_at=now,
        last_activity_at=now,
        finished_at=None,
        created_at=now,
        test_suite_id=UUID(suite_id),
    )


async def test_a_suite_run_takes_the_ready_cases_in_suite_order_with_their_story(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    ordered_ids = [world.case_ids[2], world.case_ids[0], world.case_ids[3], world.case_ids[1]]
    await seed_suite(client, world, case_ids=ordered_ids)
    recording_live_event_publisher.events.clear()

    content = await start_suite_run_content(client, world.runner.token, DEFAULT_SUITE_NAME.upper())

    assert content.keys() == {"run_id", "environment", "base_url", "health_check_url", "cases", "suite"}
    assert content["suite"] == DEFAULT_SUITE_NAME
    cases = content["cases"]
    assert isinstance(cases, list)
    assert [case["case_id"] for case in cases] == [str(case_id) for case_id in ordered_ids]
    assert [case["story_key"] for case in cases] == [
        world.second_story.jira_key,
        world.first_story.jira_key,
        world.second_story.jira_key,
        world.first_story.jira_key,
    ]
    assert cases[0].keys() == {"case_id", "code", "title", "version", "preconditions", "steps", "story_key"}
    async with container.database.begin():
        run = await container.database.get_current_session().scalar(
            select(RunTable).where(RunTable.id == UUID(str(content["run_id"])))
        )
    assert run is not None
    assert (run.story_id, run.executor, run.status) == (None, RunExecutor.CLAUDE, RunStatus.RUNNING)
    assert run.test_suite_id is not None
    event_types = [event.type for event in recording_live_event_publisher.events]
    assert event_types == [LiveEventType.RUN_STARTED]
    assert recording_live_event_publisher.events[0].ids == {
        "runId": content["run_id"],
        "suiteId": str(run.test_suite_id),
    }


async def test_a_suite_run_never_changes_a_story_test_status(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await seed_suite(client, world)

    content = await start_suite_run_content(client, world.runner.token, DEFAULT_SUITE_NAME)
    run_id = str(content["run_id"])
    for case_id in world.case_ids:
        read_tool_json(await record_suite_case(client, world.runner.token, run_id, case_id, "passed"))
    read_tool_json(await finish(client, world.runner.token, run_id))

    assert await find_story_test_status(container, world.first_story.story_id) is StoryTestStatus.NOT_STARTED
    assert await find_story_test_status(container, world.second_story.story_id) is StoryTestStatus.NOT_STARTED


async def test_a_running_suite_run_blocks_sign_off_of_the_stories_it_holds(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await seed_suite(client, world, case_ids=world.first_story.case_ids)
    for story in (world.first_story, world.second_story):
        await set_story_test_status(container, story.story_id, StoryTestStatus.IN_TEST)
    run_id = str((await start_suite_run_content(client, world.runner.token, DEFAULT_SUITE_NAME))["run_id"])

    held_story = await put_story_test_status(client, world, world.first_story.jira_key, "passed")
    other_story = await put_story_test_status(client, world, world.second_story.jira_key, "passed")
    for case_id in world.first_story.case_ids:
        read_tool_json(await record_suite_case(client, world.runner.token, run_id, case_id, "passed"))
    read_tool_json(await finish(client, world.runner.token, run_id))
    after_finish = await put_story_test_status(client, world, world.first_story.jira_key, "passed")

    assert (held_story.status_code, held_story.json()["code"]) == (409, "STORY_SIGN_OFF_BLOCKED")
    assert other_story.status_code == 200, other_story.text
    assert after_finish.status_code == 200, after_finish.text


async def test_a_suite_run_can_be_started_by_id(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)

    content = await start_suite_run_content(client, world.runner.token, suite_id)

    assert content["suite"] == DEFAULT_SUITE_NAME


async def test_needs_review_and_not_ready_cases_are_skipped_and_reported(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await flag_needs_review(container, world.case_ids[1])
    await change_case_status(container, world.case_ids[2], "draft")
    await seed_suite(client, world)

    content = await start_suite_run_content(client, world.runner.token, DEFAULT_SUITE_NAME)

    cases = content["cases"]
    assert isinstance(cases, list)
    assert [case["case_id"] for case in cases] == [str(world.case_ids[0]), str(world.case_ids[3])]
    assert content["skipped_cases"] == [
        {
            "code": await find_case_code(container, world.case_ids[1]),
            "title": "Case " + (await find_case_code(container, world.case_ids[1])).removeprefix("TC-"),
            "story_key": world.first_story.jira_key,
            "reason": "needs_review",
        },
        {
            "code": await find_case_code(container, world.case_ids[2]),
            "title": "Case " + (await find_case_code(container, world.case_ids[2])).removeprefix("TC-"),
            "story_key": world.second_story.jira_key,
            "reason": "not_ready",
        },
    ]
    run_id = str(content["run_id"])
    detail = (await client.get(f"/api/projects/{world.key}/runs/{run_id}")).json()
    assert [skipped["reason"] for skipped in detail["skippedCases"]] == ["needs_review", "not_ready"]
    read_tool_json(await record_suite_case(client, world.runner.token, run_id, world.case_ids[0]))
    read_tool_json(await finish(client, world.runner.token, run_id))
    report = (await client.get(f"/api/projects/{world.key}/runs/{run_id}")).json()["report"]
    assert [skipped["testCaseId"] for skipped in report["skippedCases"]] == [
        str(world.case_ids[1]),
        str(world.case_ids[2]),
    ]
    assert report["counts"]["total"] == 2


async def test_an_open_gap_on_one_story_blocks_the_suite_run_and_names_the_assignee(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    ba_id = await add_active_member(container, recording_mailer, world.project, ProjectRole.BA, "Bea Analyst")
    await seed_suite(client, world)
    gap_id = await raise_story_gap(client, world, world.second_story, assigneeId=str(ba_id))

    response = await start_suite_run(client, world.runner.token, DEFAULT_SUITE_NAME)

    assert read_tool_error_code(response) == "OPEN_GAPS_BLOCK_RUN"
    message = read_tool_error(response)
    assert "1 open gaps block this suite run" in message
    assert f"{world.second_story.jira_key} gap {gap_id} (assigned to Bea Analyst)" in message
    async with container.database.begin():
        run_count = await container.database.get_current_session().scalar(
            select(RunTable.id).where(RunTable.project_id == world.project.id)
        )
    assert run_count is None


async def test_a_gap_on_the_story_of_a_skipped_case_still_blocks(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await change_case_status(container, world.case_ids[2], "draft")
    await change_case_status(container, world.case_ids[3], "draft")
    await seed_suite(client, world)
    await raise_story_gap(client, world, world.second_story)

    response = await start_suite_run(client, world.runner.token, DEFAULT_SUITE_NAME)

    assert read_tool_error_code(response) == "OPEN_GAPS_BLOCK_RUN"
    assert "(assigned to the Admin role)" in read_tool_error(response)


async def test_a_suite_without_ready_cases_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    for case_id in world.case_ids:
        await flag_needs_review(container, case_id)
    await seed_suite(client, world)
    empty_world_suite = await seed_suite(client, world, name="Empty", case_ids=[])

    needs_review = await start_suite_run(client, world.runner.token, DEFAULT_SUITE_NAME)
    empty = await start_suite_run(client, world.runner.token, empty_world_suite)

    assert read_tool_error_code(needs_review) == "SUITE_EMPTY"
    assert read_tool_error_code(empty) == "SUITE_EMPTY"


async def test_one_running_run_per_suite(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await seed_suite(client, world)
    await seed_suite(client, world, name="Other", case_ids=world.case_ids[:1])
    read_tool_json(await start_suite_run(client, world.runner.token, DEFAULT_SUITE_NAME))

    second = await start_suite_run(client, world.runner.token, DEFAULT_SUITE_NAME)
    other_suite = await start_suite_run(client, world.runner.token, "Other")
    story_run = await start_run_for(client, world.runner.token, world.first_story.jira_key)

    assert read_tool_error_code(second) == "SUITE_ALREADY_RUNNING"
    read_tool_json(other_suite)
    read_tool_json(story_run)


async def test_concurrent_manual_starts_of_one_suite_open_one_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)

    responses = await asyncio.gather(
        start_manual_suite_run(client, world.key, suite_id), start_manual_suite_run(client, world.key, suite_id)
    )

    assert sorted(response.status_code for response in responses) == [201, 409]
    refused = next(response for response in responses if response.status_code == 409)
    assert refused.json()["code"] == "SUITE_ALREADY_RUNNING"


async def test_a_second_running_suite_run_that_reaches_the_database_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    async with container.database.begin():
        await container.run_repository.add(build_running_suite_run(world, suite_id))

    with pytest.raises(SuiteAlreadyRunningError):
        async with container.database.begin():
            await container.run_repository.add(build_running_suite_run(world, suite_id))


async def test_a_run_has_exactly_one_of_story_or_suite(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    both = build_running_suite_run(world, suite_id).model_copy(update={"story_id": world.first_story.story_id})
    neither = build_running_suite_run(world, suite_id).model_copy(update={"test_suite_id": None})

    for run in (both, neither):
        with pytest.raises(IntegrityError):
            async with container.database.begin():
                await container.run_repository.add(run)


async def test_start_needs_exactly_one_of_story_or_suite(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await seed_suite(client, world)

    both = await call_tool(
        client,
        world.runner.token,
        "start_run",
        {"story_key": world.first_story.jira_key, "suite": DEFAULT_SUITE_NAME},
    )
    neither = await call_tool(client, world.runner.token, "start_run", {})

    assert read_tool_error_code(both) == "INVALID_REQUEST"
    assert read_tool_error_code(neither) == "INVALID_REQUEST"


@pytest.mark.parametrize("suite", ["", "x" * 201])
async def test_an_empty_or_too_long_suite_reference_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, suite: str
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)

    refused = await start_suite_run(client, world.runner.token, suite)
    longest = await start_suite_run(client, world.runner.token, "x" * 200)

    assert "suite" in read_tool_error(refused)
    assert not read_tool_error(refused).startswith("NOT_FOUND")
    assert read_tool_error_code(longest) == "NOT_FOUND"
    async with container.database.begin():
        run_ids = await container.database.get_current_session().scalars(
            select(RunTable.id).where(RunTable.project_id == world.project.id)
        )
        assert list(run_ids) == []


async def test_unknown_and_archived_suites_are_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    assert (await archive_suite(client, world.key, suite_id)).status_code == 200

    unknown = await start_suite_run(client, world.runner.token, "Nightly")
    archived_by_name = await start_suite_run(client, world.runner.token, DEFAULT_SUITE_NAME)
    archived_manual = await start_manual_suite_run(client, world.key, suite_id)

    assert read_tool_error_code(unknown) == "NOT_FOUND"
    assert read_tool_error_code(archived_by_name) == "SUITE_ARCHIVED"
    assert (archived_manual.status_code, archived_manual.json()["code"]) == (409, "SUITE_ARCHIVED")


async def test_chosen_case_ids_must_be_ready_cases_of_the_suite(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await flag_needs_review(container, world.case_ids[1])
    await seed_suite(client, world, case_ids=world.case_ids[:3])

    picked = await start_suite_run_content(
        client, world.runner.token, DEFAULT_SUITE_NAME, case_ids=[str(world.case_ids[2]), str(world.case_ids[0])]
    )
    read_tool_json(await finish(client, world.runner.token, str(picked["run_id"])))
    outside = await start_suite_run(client, world.runner.token, DEFAULT_SUITE_NAME, case_ids=[str(world.case_ids[3])])
    needs_review = await start_suite_run(
        client, world.runner.token, DEFAULT_SUITE_NAME, case_ids=[str(world.case_ids[1])]
    )

    cases = picked["cases"]
    assert isinstance(cases, list)
    assert [case["case_id"] for case in cases] == [str(world.case_ids[2]), str(world.case_ids[0])]
    assert "skipped_cases" not in picked
    assert read_tool_error_code(outside) == "UNKNOWN_REFERENCE"
    assert read_tool_error_code(needs_review) == "CASE_NOT_READY"


async def test_finish_groups_the_report_by_story_and_notifies_with_the_suite(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    content = await start_suite_run_content(client, world.runner.token, DEFAULT_SUITE_NAME)
    run_id = str(content["run_id"])
    statuses = ["passed", "failed", "passed", "blocked"]
    for case_id, status in zip(world.case_ids, statuses, strict=True):
        read_tool_json(await record_suite_case(client, world.runner.token, run_id, case_id, status))
    recording_live_event_publisher.events.clear()

    finished = read_tool_json(await finish(client, world.runner.token, run_id))

    assert finished["status"] == "failed"
    report = (await client.get(f"/api/projects/{world.key}/runs/{run_id}")).json()["report"]
    assert [
        (story["storyJiraKey"], story["counts"]["total"], story["counts"]["passed"], story["counts"]["failed"])
        for story in report["stories"]
    ] == [(world.first_story.jira_key, 2, 1, 1), (world.second_story.jira_key, 2, 1, 0)]
    assert report["stories"][1]["counts"]["blocked"] == 1
    assert [failed["storyJiraKey"] for failed in report["failedCases"]] == [
        world.first_story.jira_key,
        world.second_story.jira_key,
    ]
    finished_events = [
        event for event in recording_live_event_publisher.events if event.type is LiveEventType.RUN_FINISHED
    ]
    assert finished_events[0].ids == {"runId": run_id, "suiteId": suite_id, "status": "failed"}
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(NotificationTable).where(NotificationTable.project_id == world.project.id)
        )
        payloads = [row.payload for row in rows if row.payload.get("run_id") == run_id]
    assert payloads == [
        {
            "kind": "suite_run_finished",
            "run_id": run_id,
            "test_suite_id": suite_id,
            "test_suite_name": DEFAULT_SUITE_NAME,
            "outcome": "failed",
            "passed_count": 2,
            "failed_count": 1,
            "blocked_count": 1,
        }
    ]


async def test_a_recorded_suite_case_publishes_its_own_story_and_the_suite(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    run_id = str((await start_suite_run_content(client, world.runner.token, DEFAULT_SUITE_NAME))["run_id"])
    recording_live_event_publisher.events.clear()

    recorded = read_tool_json(await record_suite_case(client, world.runner.token, run_id, world.case_ids[3]))

    event = recording_live_event_publisher.events[0]
    assert event.type is LiveEventType.RUN_CASE_RECORDED
    assert event.ids == {
        "runId": run_id,
        "caseResultId": recorded["case_result_id"],
        "testCaseId": str(world.case_ids[3]),
        "storyId": str(world.second_story.story_id),
        "suiteId": suite_id,
    }


async def test_failed_cases_of_a_suite_run_name_the_suite_and_each_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await seed_suite(client, world)
    run_id = str((await start_suite_run_content(client, world.runner.token, DEFAULT_SUITE_NAME))["run_id"])
    for case_id, status in zip(world.case_ids, ["passed", "failed", "passed", "blocked"], strict=True):
        read_tool_json(await record_suite_case(client, world.runner.token, run_id, case_id, status))
    read_tool_json(await finish(client, world.runner.token, run_id))

    failed = read_tool_json(await call_tool(client, world.runner.token, "get_failed_cases", {"run_id": run_id}))

    assert failed.keys() == {"run_id", "run_status", "suite", "environment", "cases"}
    assert failed["suite"] == DEFAULT_SUITE_NAME
    assert failed["cases"] == [
        {
            "case_id": str(world.case_ids[1]),
            "code": await find_case_code(container, world.case_ids[1]),
            "title": "Case " + (await find_case_code(container, world.case_ids[1])).removeprefix("TC-"),
            "status": "failed",
            "story_key": world.first_story.jira_key,
        },
        {
            "case_id": str(world.case_ids[3]),
            "code": await find_case_code(container, world.case_ids[3]),
            "title": "Case " + (await find_case_code(container, world.case_ids[3])).removeprefix("TC-"),
            "status": "blocked",
            "story_key": world.second_story.jira_key,
        },
    ]


async def test_claude_reruns_the_failed_cases_of_a_suite_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await seed_suite(client, world)
    await seed_suite(client, world, name="Other", case_ids=world.case_ids[:1])
    parent_id = str((await start_suite_run_content(client, world.runner.token, DEFAULT_SUITE_NAME))["run_id"])
    for case_id, status in zip(world.case_ids, ["passed", "failed", "passed", "blocked"], strict=True):
        read_tool_json(await record_suite_case(client, world.runner.token, parent_id, case_id, status))
    read_tool_json(await finish(client, world.runner.token, parent_id))
    await flag_needs_review(container, world.case_ids[3])

    wrong_suite = await start_suite_run(client, world.runner.token, "Other", parent_run_id=parent_id)
    wrong_story = await start_run_for(client, world.runner.token, world.first_story.jira_key, parent_run_id=parent_id)
    rerun = await start_suite_run_content(client, world.runner.token, DEFAULT_SUITE_NAME, parent_run_id=parent_id)

    assert read_tool_error_code(wrong_suite) == "INVALID_REQUEST"
    assert read_tool_error_code(wrong_story) == "INVALID_REQUEST"
    cases = rerun["cases"]
    assert isinstance(cases, list)
    assert [case["case_id"] for case in cases] == [str(world.case_ids[1])]
    detail = (await client.get(f"/api/projects/{world.key}/runs/{rerun['run_id']}")).json()
    assert detail["parentRunId"] == parent_id


async def test_a_manual_suite_run_is_recorded_finished_and_rerun(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)

    started = await start_manual_suite_run(client, world.key, suite_id)

    assert started.status_code == 201, started.text
    body = started.json()
    assert (body["storyId"], body["testSuiteId"], body["executor"]) == (None, suite_id, "manual")
    assert [case["testCaseId"] for case in body["cases"]] == [str(case_id) for case_id in world.case_ids]
    run_id = body["id"]
    for case_id, status in zip(world.case_ids, ["passed", "failed", "passed", "passed"], strict=True):
        recorded = await client.put(
            f"/api/projects/{world.key}/runs/{run_id}/cases/{case_id}",
            json={"steps": [{"order": 1, "status": status}, {"order": 2, "status": status}]},
        )
        assert recorded.status_code == 200, recorded.text
    finished = await client.post(f"/api/projects/{world.key}/runs/{run_id}/finish", json={})
    assert finished.json()["status"] == "failed"
    rerun = await client.post(f"/api/projects/{world.key}/runs/{run_id}/rerun-failed")
    assert rerun.status_code == 201, rerun.text
    assert (rerun.json()["testSuiteId"], rerun.json()["parentRunId"]) == (suite_id, run_id)
    assert [case["testCaseId"] for case in rerun.json()["cases"]] == [str(world.case_ids[1])]


async def test_a_manual_run_needs_exactly_one_of_story_or_suite(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)

    both = await start_manual_suite_run(client, world.key, suite_id, storyKey=world.first_story.jira_key)
    neither = await client.post(f"/api/projects/{world.key}/runs", json={})

    assert (both.status_code, both.json()["code"]) == (422, "INVALID_REQUEST")
    assert (neither.status_code, neither.json()["code"]) == (422, "INVALID_REQUEST")


async def test_a_dev_starts_claude_suite_runs_but_not_manual_ones(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer, ProjectRole.DEV)
    qc = await sign_up_runner(client, container, recording_mailer, world.project, ProjectRole.QC, "Quinn QC")
    use_session(client, qc.account.session_token)
    suite_id = await seed_suite(client, world)
    use_session(client, world.runner.account.session_token)

    manual = await start_manual_suite_run(client, world.key, suite_id)
    claude = await start_suite_run(client, world.runner.token, DEFAULT_SUITE_NAME)

    assert (manual.status_code, manual.json()["code"]) == (403, "PERMISSION_DENIED")
    read_tool_json(claude)

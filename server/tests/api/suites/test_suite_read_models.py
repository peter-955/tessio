from datetime import UTC, datetime, timedelta
from uuid import UUID

from httpx import AsyncClient
from sqlalchemy import select, update

from app.container import Container
from app.modules.failures.infrastructure import FailureTable
from app.modules.insights.infrastructure import PostgresCoverageReader
from app.modules.insights.usecases.criterion_impact_calculator import LatestResultCriterionImpactCalculator
from app.modules.notifications.infrastructure import NotificationTable
from app.modules.runs.infrastructure import RunTable
from app.shared.events import LiveEventType
from tests.api.runs.run_steps import finish, start_run_id
from tests.api.suites.suite_steps import (
    DEFAULT_SUITE_NAME,
    SuiteWorld,
    find_case_code,
    link_criterion,
    put_stories_in_active_sprint,
    record_suite_case,
    run_suite_with,
    seed_suite,
    seed_suite_world,
)
from tests.conftest import RecordingMailer
from tests.support.mcp_steps import read_tool_json
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def seed_finished_suite_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, statuses: list[str]
) -> tuple[SuiteWorld, str, str]:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    run_id = await run_suite_with(client, world, statuses)
    read_tool_json(await finish(client, world.runner.token, run_id))
    return world, suite_id, run_id


async def test_run_list_shows_the_suite_and_filters_by_it(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world, suite_id, suite_run_id = await seed_finished_suite_run(
        client, container, recording_mailer, ["passed", "failed", "passed", "passed"]
    )
    story_run_id = await start_run_id(client, world.runner.token, world.first_story.jira_key)
    runs_url = f"/api/projects/{world.key}/runs"

    every_run = (await client.get(runs_url)).json()
    suite_runs = (await client.get(runs_url, params={"suiteId": suite_id})).json()
    story_runs = (await client.get(runs_url, params={"storyKey": world.first_story.jira_key})).json()

    assert [run["id"] for run in every_run] == [story_run_id, suite_run_id]
    suite_run = every_run[1]
    assert (suite_run["storyId"], suite_run["storyJiraKey"], suite_run["storyTitle"]) == (None, None, None)
    assert (suite_run["testSuiteId"], suite_run["testSuiteName"]) == (suite_id, DEFAULT_SUITE_NAME)
    assert suite_run["counts"]["total"] == 4
    assert suite_run["counts"]["failed"] == 1
    assert every_run[0]["testSuiteId"] is None
    assert every_run[0]["storyJiraKey"] == world.first_story.jira_key
    assert [run["id"] for run in suite_runs] == [suite_run_id]
    assert [run["id"] for run in story_runs] == [story_run_id]


async def test_run_detail_names_each_case_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world, suite_id, run_id = await seed_finished_suite_run(
        client, container, recording_mailer, ["passed", "passed", "failed", "passed"]
    )

    detail = (await client.get(f"/api/projects/{world.key}/runs/{run_id}")).json()

    assert (detail["testSuiteId"], detail["testSuiteName"], detail["storyJiraKey"]) == (
        suite_id,
        DEFAULT_SUITE_NAME,
        None,
    )
    assert [case["storyJiraKey"] for case in detail["cases"]] == [
        world.first_story.jira_key,
        world.first_story.jira_key,
        world.second_story.jira_key,
        world.second_story.jira_key,
    ]
    assert detail["cases"][2]["storyId"] == str(world.second_story.story_id)
    assert detail["skippedCases"] == []
    assert [story["storyJiraKey"] for story in detail["report"]["stories"]] == [
        world.first_story.jira_key,
        world.second_story.jira_key,
    ]


async def test_a_story_run_detail_also_names_the_story_of_its_cases(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    run_id = await start_run_id(client, world.runner.token, world.first_story.jira_key)

    detail = (await client.get(f"/api/projects/{world.key}/runs/{run_id}")).json()

    assert (detail["testSuiteId"], detail["testSuiteName"]) == (None, None)
    assert {case["storyJiraKey"] for case in detail["cases"]} == {world.first_story.jira_key}


async def test_suite_results_count_in_the_dashboard_and_traceability_of_each_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await put_stories_in_active_sprint(container, world)
    first_criterion_id = await link_criterion(container, world.first_story.story_id, world.first_story.case_ids)
    await link_criterion(container, world.second_story.story_id, world.second_story.case_ids)
    await seed_suite(client, world)
    run_id = await run_suite_with(client, world, ["passed", "passed", "failed", "passed"])
    read_tool_json(await finish(client, world.runner.token, run_id))

    dashboard = (await client.get(f"/api/projects/{world.key}/dashboard")).json()
    traceability = (
        await client.get(f"/api/projects/{world.key}/stories/{world.first_story.jira_key}/traceability")
    ).json()

    assert dashboard["storyCount"] == 2
    assert dashboard["testStatusCounts"]["notStarted"] == 2
    assert dashboard["testStatusCounts"]["inTest"] == 0
    assert (dashboard["coverage"]["passedCount"], dashboard["coverage"]["failedCount"]) == (1, 1)
    assert dashboard["activeFailureCount"] == 1
    latest_results = {case["id"]: case["latestResult"] for case in traceability["cases"]}
    assert {result["runId"] for result in latest_results.values()} == {run_id}
    assert {result["status"] for result in latest_results.values()} == {"passed"}
    criteria = {criterion["id"]: criterion for criterion in traceability["criteria"]}
    assert criteria[str(first_criterion_id)]["status"] == "passed"


async def test_story_progress_counts_suite_results_and_shows_the_suite_run_as_last_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await link_criterion(container, world.first_story.story_id, world.first_story.case_ids)
    await link_criterion(container, world.second_story.story_id, world.second_story.case_ids)
    older_story_run_id = await start_run_id(client, world.runner.token, world.second_story.jira_key)
    read_tool_json(await finish(client, world.runner.token, older_story_run_id))
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(RunTable)
            .where(RunTable.id == UUID(older_story_run_id))
            .values(started_at=datetime.now(UTC) - timedelta(hours=2))
        )
    await seed_suite(client, world, case_ids=world.first_story.case_ids)
    run_id = await run_suite_with(client, world, ["failed", "passed"])
    read_tool_json(await finish(client, world.runner.token, run_id))

    progress = (await client.get(f"/api/projects/{world.key}/story-progress")).json()

    by_key = {story["jiraKey"]: story for story in progress}
    first = by_key[world.first_story.jira_key]
    assert first["lastRun"]["id"] == run_id
    assert first["lastRun"]["status"] == "failed"
    assert (first["coverage"]["failedCount"], first["activeFailureCount"]) == (1, 1)
    assert by_key[world.second_story.jira_key]["lastRun"]["id"] == older_story_run_id


async def test_a_suite_failure_opens_on_the_case_story_and_reaches_my_work(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world, _, run_id = await seed_finished_suite_run(
        client, container, recording_mailer, ["passed", "passed", "passed", "failed"]
    )

    failures = (await client.get(f"/api/projects/{world.key}/failures")).json()
    my_work = (await client.get(f"/api/projects/{world.key}/my-work")).json()

    assert len(failures) == 1
    failure = failures[0]
    assert failure["storyId"] == str(world.second_story.story_id)
    assert failure["storyJiraKey"] == world.second_story.jira_key
    assert failure["testCaseCode"] == await find_case_code(container, world.case_ids[3])
    assert failure["latestRunId"] == run_id
    assert my_work["unassignedFailureCount"] == 1
    async with container.database.begin():
        story_ids = await container.database.get_current_session().scalars(
            select(FailureTable.story_id).where(FailureTable.project_id == world.project.id)
        )
    assert list(story_ids) == [world.second_story.story_id]


async def test_the_notification_list_carries_the_suite_run_payload(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    _, suite_id, run_id = await seed_finished_suite_run(
        client, container, recording_mailer, ["passed", "passed", "passed", "passed"]
    )

    notifications = (await client.get("/api/notifications")).json()

    items = [item for item in notifications["items"] if item["kind"] == "suite_run_finished"]
    assert [item["payload"] for item in items] == [
        {
            "kind": "suite_run_finished",
            "runId": run_id,
            "testSuiteId": suite_id,
            "testSuiteName": DEFAULT_SUITE_NAME,
            "outcome": "passed",
            "passedCount": 4,
            "failedCount": 0,
            "blockedCount": 0,
        }
    ]


async def test_a_stale_suite_run_is_aborted_and_announced_with_the_suite(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    run_id = await run_suite_with(client, world, ["passed"])
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(RunTable)
            .where(RunTable.id == UUID(run_id))
            .values(last_activity_at=datetime.now(UTC) - timedelta(hours=5))
        )
    recording_live_event_publisher.events.clear()

    aborted_count = await container.abort_stale_runs.execute(datetime.now(UTC))

    assert aborted_count == 1
    detail = (await client.get(f"/api/projects/{world.key}/runs/{run_id}")).json()
    assert (detail["status"], detail["abortReason"]) == ("aborted", "inactive")
    assert detail["report"]["stories"][0]["counts"]["passed"] == 1
    finished_events = [
        event for event in recording_live_event_publisher.events if event.type is LiveEventType.RUN_FINISHED
    ]
    assert [event.ids for event in finished_events] == [{"runId": run_id, "suiteId": suite_id, "status": "aborted"}]
    async with container.database.begin():
        rows = await container.database.get_current_session().scalars(
            select(NotificationTable).where(NotificationTable.project_id == world.project.id)
        )
        kinds = {row.kind.value for row in rows if row.payload.get("run_id") == run_id}
    assert kinds == {"suite_run_finished"}


async def test_the_run_log_of_a_suite_run_is_accepted_and_read(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world, _, run_id = await seed_finished_suite_run(
        client, container, recording_mailer, ["passed", "passed", "passed", "passed"]
    )

    uploaded = await client.post(
        f"/api/runs/{run_id}/log",
        headers={"authorization": f"Bearer {world.runner.token}"},
        json={"entries": []},
    )
    log = await client.get(f"/api/projects/{world.key}/runs/{run_id}/log")

    assert uploaded.status_code in {200, 201, 204}, uploaded.text
    assert log.status_code == 200, log.text
    assert log.json()["receivedAt"] is not None


async def test_criterion_impact_of_a_suite_run_lists_the_touched_criteria_by_story(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    await link_criterion(container, world.first_story.story_id, world.first_story.case_ids[:1])
    await link_criterion(container, world.second_story.story_id, world.second_story.case_ids, "AC-1")
    await link_criterion(container, world.second_story.story_id, [], "AC-9", position=2)
    await seed_suite(client, world)
    run_id = await run_suite_with(client, world, ["passed", "passed", "failed"])
    calculator = LatestResultCriterionImpactCalculator(container.database, PostgresCoverageReader(container.database))

    impacts = await calculator.calculate(world.project.id, UUID(run_id))

    assert [(impact.story_jira_key, impact.code, impact.status.value) for impact in impacts] == [
        (world.first_story.jira_key, "AC-1", "passed"),
        (world.second_story.jira_key, "AC-1", "failed"),
    ]
    assert impacts[1].failed_case_codes == [await find_case_code(container, world.case_ids[2])]
    read_tool_json(await record_suite_case(client, world.runner.token, run_id, world.case_ids[3]))
    read_tool_json(await finish(client, world.runner.token, run_id))
    report = (await client.get(f"/api/projects/{world.key}/runs/{run_id}")).json()["report"]
    assert [impact["storyJiraKey"] for impact in report["criterionImpacts"]] == [
        world.first_story.jira_key,
        world.second_story.jira_key,
    ]

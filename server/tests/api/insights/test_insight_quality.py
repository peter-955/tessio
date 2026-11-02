from datetime import timedelta
from uuid import uuid7

from httpx import AsyncClient

from app.container import Container
from app.modules.runs import ResultStatus
from app.modules.stories import SprintState
from app.modules.test_cases import TestCaseStatus as CaseStatus
from tests.api.insights.insight_steps import (
    BASE_TIME,
    InsightWorld,
    get_ok,
    seed_case,
    seed_sprint,
    seed_story,
    sign_in_world,
)
from tests.api.insights.trend_steps import (
    mark_case_quality,
    seed_any_run,
    seed_iteration_result,
    seed_label,
    seed_run_log,
    seed_suite,
)
from tests.conftest import RecordingMailer

RANGE = {"from": "2026-10-01", "to": "2026-10-03"}


def insights_path(world: InsightWorld, name: str) -> str:
    return f"/api/projects/{world.project.key}/insights/{name}"


async def test_coverage_by_label_counts_cases_ready_and_passed(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world)
    passing_case = await seed_case(container, world, story)
    failing_case = await seed_case(container, world, story)
    draft_case = await seed_case(container, world, story, status=CaseStatus.DRAFT)
    deprecated_case = await seed_case(container, world, story, status=CaseStatus.DEPRECATED)
    unlabelled_case = await seed_case(container, world, story)
    checkout_label = await seed_label(
        container, world, "Checkout", (passing_case, failing_case, draft_case, deprecated_case)
    )
    empty_label = await seed_label(container, world, "Empty", ())
    suite_id = await seed_suite(container, world, f"Regression {uuid7().hex[:6]}")
    story_run = await seed_any_run(container, world, (passing_case, failing_case), BASE_TIME, story=story)
    await seed_iteration_result(container, world, story_run, passing_case, ResultStatus.FAILED, BASE_TIME)
    await seed_iteration_result(container, world, story_run, failing_case, ResultStatus.FAILED, BASE_TIME)
    later = BASE_TIME + timedelta(hours=2)
    suite_run = await seed_any_run(
        container, world, (passing_case, unlabelled_case), later, executor="ci", suite_id=suite_id
    )
    await seed_iteration_result(container, world, suite_run, passing_case, ResultStatus.PASSED, later)
    await seed_iteration_result(container, world, suite_run, unlabelled_case, ResultStatus.PASSED, later)

    body = (await get_ok(client, insights_path(world, "coverage-by-label"))).json()

    assert body["labels"] == [
        {
            "labelId": str(checkout_label),
            "name": "Checkout",
            "color": "blue",
            "counts": {
                "caseCount": 3,
                "readyCount": 2,
                "passedCount": 1,
                "readyShare": 0.6667,
                "passedShare": 0.3333,
            },
        },
        {
            "labelId": str(empty_label),
            "name": "Empty",
            "color": "blue",
            "counts": {"caseCount": 0, "readyCount": 0, "passedCount": 0, "readyShare": None, "passedShare": None},
        },
    ]
    assert body["unlabelled"] == {
        "caseCount": 1,
        "readyCount": 1,
        "passedCount": 1,
        "readyShare": 1.0,
        "passedShare": 1.0,
    }
    assert body["total"]["caseCount"] == 4
    assert body["total"]["passedCount"] == 2


async def test_top_failing_counts_story_and_suite_runs_with_the_worst_iteration(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world)
    often_failing = await seed_case(container, world, story)
    data_driven = await seed_case(container, world, story)
    blocked_once = await seed_case(container, world, story)
    always_passing = await seed_case(container, world, story)
    suite_id = await seed_suite(container, world, f"Regression {uuid7().hex[:6]}")
    first_run = await seed_any_run(
        container, world, (often_failing, data_driven, blocked_once, always_passing), BASE_TIME, story=story
    )
    await seed_iteration_result(container, world, first_run, often_failing, ResultStatus.FAILED, BASE_TIME)
    await seed_iteration_result(container, world, first_run, data_driven, ResultStatus.PASSED, BASE_TIME, 0)
    await seed_iteration_result(container, world, first_run, data_driven, ResultStatus.FAILED, BASE_TIME, 1)
    await seed_iteration_result(container, world, first_run, blocked_once, ResultStatus.BLOCKED, BASE_TIME)
    await seed_iteration_result(container, world, first_run, always_passing, ResultStatus.PASSED, BASE_TIME)
    second_day = BASE_TIME + timedelta(days=1)
    suite_run = await seed_any_run(
        container, world, (often_failing, data_driven), second_day, executor="ci", suite_id=suite_id
    )
    await seed_iteration_result(container, world, suite_run, often_failing, ResultStatus.FAILED, second_day)
    await seed_iteration_result(container, world, suite_run, data_driven, ResultStatus.PASSED, second_day)
    outside = BASE_TIME + timedelta(days=10)
    late_run = await seed_any_run(container, world, (always_passing,), outside, story=story)
    await seed_iteration_result(container, world, late_run, always_passing, ResultStatus.FAILED, outside)
    await mark_case_quality(container, often_failing, flaky_score=3, flaky_since=BASE_TIME)

    body = (await get_ok(client, insights_path(world, "top-failing"), RANGE)).json()

    assert [
        (item["code"], item["resultCount"], item["failedCount"], item["blockedCount"], item["failRate"])
        for item in body
    ] == [
        (often_failing.code, 2, 2, 0, 1.0),
        (blocked_once.code, 1, 0, 1, 1.0),
        (data_driven.code, 2, 1, 0, 0.5),
    ]
    assert body[0]["isFlaky"] is True
    assert body[0]["storyJiraKey"] == story.jira_key
    assert len((await get_ok(client, insights_path(world, "top-failing"), {**RANGE, "limit": "1"})).json()) == 1


async def test_flaky_lists_flaky_and_disagreeing_cases_by_score(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world)
    most_flaky = await seed_case(container, world, story)
    disagreeing = await seed_case(container, world, story)
    quarantined = await seed_case(container, world, story)
    deprecated = await seed_case(container, world, story, status=CaseStatus.DEPRECATED)
    await seed_case(container, world, story)
    await mark_case_quality(container, most_flaky, flaky_score=5, flaky_since=BASE_TIME)
    await mark_case_quality(container, disagreeing, disagreed_at=BASE_TIME)
    await mark_case_quality(container, quarantined, flaky_score=3, flaky_since=BASE_TIME, quarantined_at=BASE_TIME)
    await mark_case_quality(container, deprecated, flaky_score=9, flaky_since=BASE_TIME)

    body = (await get_ok(client, insights_path(world, "flaky"))).json()

    assert [
        (item["code"], item["flakyScore"], item["isFlaky"], item["isDisagreeing"], item["isQuarantined"])
        for item in body
    ] == [
        (most_flaky.code, 5, True, False, False),
        (quarantined.code, 3, True, False, True),
        (disagreeing.code, 0, False, True, False),
    ]


async def test_tokens_come_from_run_logs_in_the_range(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world)
    first_case = await seed_case(container, world, story)
    second_case = await seed_case(container, world, story)
    suite_name = f"Regression {uuid7().hex[:6]}"
    suite_id = await seed_suite(container, world, suite_name)
    story_run = await seed_any_run(container, world, (first_case, second_case), BASE_TIME, story=story)
    await seed_run_log(container, story_run, 1000, 500, cache_read_input_tokens=2000)
    suite_run = await seed_any_run(container, world, (first_case,), BASE_TIME + timedelta(days=1), suite_id=suite_id)
    await seed_run_log(container, suite_run, 100, 50)
    await seed_any_run(container, world, (first_case,), BASE_TIME, executor="manual", story=story)
    outside_run = await seed_any_run(container, world, (first_case,), BASE_TIME + timedelta(days=20), story=story)
    await seed_run_log(container, outside_run, 9000, 9000)

    body = (await get_ok(client, insights_path(world, "tokens"), RANGE)).json()

    assert [(run["runId"], run["totalTokens"], run["tokensPerCase"]) for run in body["runs"]] == [
        (str(suite_run), 150, 150),
        (str(story_run), 3500, 1750),
    ]
    assert body["runs"][0]["testSuiteName"] == suite_name
    assert body["runs"][1]["storyJiraKey"] == story.jira_key
    assert body["runs"][1]["cacheReadInputTokens"] == 2000
    assert (body["totalTokens"], body["meanTokensPerRun"], body["meanTokensPerCase"]) == (3650, 1825, 1217)


async def test_tokens_leave_out_runs_whose_log_reported_no_usage(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world)
    seeded_case = await seed_case(container, world, story)
    reported_run = await seed_any_run(container, world, (seeded_case,), BASE_TIME, story=story)
    await seed_run_log(container, reported_run, 300, 100)
    unreported_run = await seed_any_run(container, world, (seeded_case,), BASE_TIME + timedelta(hours=1), story=story)
    await seed_run_log(container, unreported_run, 0, 0)

    body = (await get_ok(client, insights_path(world, "tokens"), RANGE)).json()

    assert [run["runId"] for run in body["runs"]] == [str(reported_run)]
    assert (body["totalTokens"], body["meanTokensPerRun"], body["meanTokensPerCase"]) == (400, 400, 400)


async def test_sprint_coverage_counts_the_ac_of_each_sprint(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    sprint_id = await seed_sprint(container, world, SprintState.ACTIVE, BASE_TIME)
    story = await seed_story(container, world, sprint_id, ("AC1", "AC2"))
    seeded_case = await seed_case(container, world, story, criterion_codes=("AC1",))
    run_id = await seed_any_run(container, world, (seeded_case,), BASE_TIME, story=story)
    await seed_iteration_result(container, world, run_id, seeded_case, ResultStatus.PASSED, BASE_TIME)
    await seed_sprint(container, world, SprintState.FUTURE, BASE_TIME + timedelta(days=60))

    body = (await get_ok(client, insights_path(world, "sprint-coverage"), RANGE)).json()

    assert len(body) == 1
    assert body[0]["sprint"]["id"] == str(sprint_id)
    assert body[0]["storyCount"] == 1
    assert body[0]["coverage"]["criterionCount"] == 2
    assert body[0]["coverage"]["coveredCount"] == 1
    assert body[0]["coverage"]["passedCount"] == 1

from datetime import UTC, date, datetime, timedelta
from uuid import UUID, uuid7

from httpx import AsyncClient
from sqlalchemy import insert

from app.container import Container
from app.modules.failures.typing.enums import FailureStatus
from app.modules.insights.domains.daily_stats.entity import DailyStats
from app.modules.runs import ResultStatus
from app.modules.stories import SprintState
from app.modules.stories.infrastructure import SprintTable
from tests.api.insights.insight_steps import (
    BASE_TIME,
    FAILURE_ROWS,
    InsightWorld,
    SeededCase,
    get_ok,
    seed_case,
    seed_gap,
    seed_story,
    sign_in_world,
)
from tests.api.insights.trend_steps import (
    answer_gap,
    seed_any_run,
    seed_failure_status_event,
    seed_iteration_result,
    seed_suite,
)
from tests.conftest import RecordingMailer

FIRST_DAY = BASE_TIME.date()
HOUR = timedelta(hours=1)


def trends_path(world: InsightWorld) -> str:
    return f"/api/projects/{world.project.key}/insights/trends"


async def seed_failure_row(
    container: Container, world: InsightWorld, seeded_case: SeededCase, case_result_id: UUID, created_at: datetime
) -> UUID:
    failure_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(FAILURE_ROWS).values(
                id=failure_id,
                project_id=world.project.id,
                story_id=seeded_case.story_id,
                test_case_id=seeded_case.id,
                opened_by_case_result_id=case_result_id,
                latest_case_result_id=case_result_id,
                assignee_id=None,
                status=FailureStatus.FIXED.value,
                created_at=created_at,
            )
        )
    return failure_id


async def seed_sprint_window(
    container: Container, world: InsightWorld, name: str, start_at: datetime, end_at: datetime
) -> UUID:
    sprint_id = uuid7()
    async with container.database.begin():
        await container.database.get_current_session().execute(
            insert(SprintTable).values(
                id=sprint_id,
                project_id=world.project.id,
                jira_sprint_id=world.next_jira_sprint_id(),
                name=name,
                state=SprintState.CLOSED,
                start_at=start_at,
                end_at=end_at,
                complete_at=None,
                synced_at=datetime.now(UTC),
                created_at=datetime.now(UTC),
            )
        )
    return sprint_id


async def seed_three_days(client: AsyncClient, container: Container, recording_mailer: RecordingMailer) -> InsightWorld:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world)
    first_case = await seed_case(container, world, story)
    second_case = await seed_case(container, world, story)
    third_case = await seed_case(container, world, story)
    claude_run = await seed_any_run(container, world, (first_case, second_case), BASE_TIME, story=story)
    await seed_iteration_result(container, world, claude_run, first_case, ResultStatus.PASSED, BASE_TIME)
    failed_result = await seed_iteration_result(
        container, world, claude_run, second_case, ResultStatus.FAILED, BASE_TIME
    )
    manual_run = await seed_any_run(
        container, world, (first_case, third_case), BASE_TIME + HOUR, executor="manual", story=story
    )
    await seed_iteration_result(container, world, manual_run, first_case, ResultStatus.PASSED, BASE_TIME + HOUR, 0)
    await seed_iteration_result(container, world, manual_run, first_case, ResultStatus.FAILED, BASE_TIME + HOUR, 1)
    await seed_iteration_result(container, world, manual_run, third_case, ResultStatus.SKIPPED, BASE_TIME + HOUR)
    suite_id = await seed_suite(container, world, f"Regression {uuid7().hex[:6]}")
    second_day = BASE_TIME + timedelta(days=1)
    suite_run = await seed_any_run(
        container, world, (first_case, second_case), second_day, executor="ci", suite_id=suite_id
    )
    await seed_iteration_result(container, world, suite_run, first_case, ResultStatus.PASSED, second_day)
    await seed_iteration_result(container, world, suite_run, second_case, ResultStatus.BLOCKED, second_day)
    failure_id = await seed_failure_row(container, world, second_case, failed_result, BASE_TIME)
    await seed_failure_status_event(container, failure_id, FailureStatus.FIXED, BASE_TIME + 30 * HOUR)
    await seed_failure_status_event(container, failure_id, FailureStatus.VERIFIED, BASE_TIME + 50 * HOUR)
    answered_gap = await seed_gap(container, world, story, created_at=BASE_TIME)
    await answer_gap(container, answered_gap, BASE_TIME + 24 * HOUR)
    await seed_gap(container, world, story, created_at=BASE_TIME + 27 * HOUR)
    return world


def read_points(body: dict[str, object]) -> list[dict[str, object]]:
    points = body["points"]
    assert isinstance(points, list)
    return points


async def test_trends_per_day_count_runs_results_failures_and_gaps(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_three_days(client, container, recording_mailer)

    body = (
        await get_ok(
            client,
            trends_path(world),
            {"from": FIRST_DAY.isoformat(), "to": (FIRST_DAY + timedelta(days=2)).isoformat()},
        )
    ).json()

    assert body["groupBy"] == "day"
    assert body["executors"] == ["claude", "manual", "ci"]
    first, second, third = read_points(body)
    assert first["day"] == "2026-10-01"
    assert first["runCount"] == 2
    assert first["runsByExecutor"] == [
        {"executor": "claude", "count": 1},
        {"executor": "manual", "count": 1},
        {"executor": "ci", "count": 0},
    ]
    assert (first["passedCount"], first["failedCount"], first["blockedCount"], first["skippedCount"]) == (1, 2, 0, 1)
    assert first["passRate"] == 0.3333
    assert (first["failuresOpened"], first["failuresFixed"], first["meanTimeToFixSeconds"]) == (1, 0, None)
    assert (first["gapsOpened"], first["gapsAnswered"]) == (1, 0)
    assert (first["openGapCount"], first["medianOpenGapAgeSeconds"]) == (1, 15 * 3600)
    assert second["runsByExecutor"] == [
        {"executor": "claude", "count": 0},
        {"executor": "manual", "count": 0},
        {"executor": "ci", "count": 1},
    ]
    assert (second["passedCount"], second["blockedCount"], second["passRate"]) == (1, 1, 0.5)
    assert (second["failuresFixed"], second["meanTimeToFixSeconds"]) == (1, 30 * 3600)
    assert (second["gapsOpened"], second["gapsAnswered"], second["meanGapAnswerSeconds"]) == (1, 1, 24 * 3600)
    assert (second["openGapCount"], second["medianOpenGapAgeSeconds"]) == (1, 12 * 3600)
    assert (third["runCount"], third["passRate"], third["failuresFixed"]) == (0, None, 0)
    assert (third["openGapCount"], third["medianOpenGapAgeSeconds"]) == (1, 36 * 3600)
    total = body["total"]
    assert isinstance(total, dict)
    assert (total["runCount"], total["passedCount"], total["failedCount"], total["blockedCount"]) == (3, 2, 2, 1)
    assert total["passRate"] == 0.4
    assert (total["failuresOpened"], total["failuresFixed"], total["openGapCount"]) == (1, 1, 1)


async def test_trends_per_sprint_group_the_days_of_each_sprint(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_three_days(client, container, recording_mailer)
    first_sprint = await seed_sprint_window(container, world, "Sprint A", BASE_TIME - 9 * HOUR, BASE_TIME + 38 * HOUR)
    second_sprint = await seed_sprint_window(
        container, world, "Sprint B", BASE_TIME + 39 * HOUR, BASE_TIME + timedelta(days=14)
    )

    body = (
        await get_ok(
            client,
            trends_path(world),
            {"from": FIRST_DAY.isoformat(), "to": (FIRST_DAY + timedelta(days=2)).isoformat(), "groupBy": "sprint"},
        )
    ).json()

    first, second = read_points(body)
    assert first["day"] is None
    assert isinstance(first["sprint"], dict)
    assert first["sprint"]["id"] == str(first_sprint)
    assert (first["firstDay"], first["lastDay"]) == ("2026-10-01", "2026-10-02")
    assert (first["runCount"], first["passedCount"], first["failedCount"], first["blockedCount"]) == (3, 2, 2, 1)
    assert (first["failuresFixed"], first["medianOpenGapAgeSeconds"]) == (1, 12 * 3600)
    assert isinstance(second["sprint"], dict)
    assert second["sprint"]["id"] == str(second_sprint)
    assert (second["firstDay"], second["lastDay"], second["runCount"]) == ("2026-10-03", "2026-10-03", 0)


async def test_trends_read_the_stored_daily_snapshot(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    stored_day = date(2026, 9, 20)
    async with container.database.begin():
        await container.daily_stats_repository.save_all(
            [
                DailyStats(
                    project_id=world.project.id,
                    day=stored_day,
                    runs_by_executor={"claude": 4},
                    passed_count=7,
                    failed_count=1,
                    blocked_count=0,
                    skipped_count=0,
                    failures_opened=1,
                    failures_fixed=0,
                    fix_seconds_total=0,
                    gaps_opened=0,
                    gaps_answered=0,
                    answer_seconds_total=0,
                    open_gap_count=2,
                    median_open_gap_age_seconds=600,
                )
            ],
            datetime.now(UTC),
        )

    body = (
        await get_ok(client, trends_path(world), {"from": stored_day.isoformat(), "to": stored_day.isoformat()})
    ).json()

    (point,) = read_points(body)
    assert (point["runCount"], point["passedCount"], point["passRate"]) == (4, 7, 0.875)
    assert (point["openGapCount"], point["medianOpenGapAgeSeconds"]) == (2, 600)


async def test_trends_default_to_the_last_thirty_days(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    today = datetime.now(UTC).date()

    body = (await get_ok(client, trends_path(world))).json()

    assert body["lastDay"] == today.isoformat()
    assert body["firstDay"] == (today - timedelta(days=29)).isoformat()
    assert len(read_points(body)) == 30


async def test_trends_refuse_a_bad_range_or_grouping(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)

    reversed_range = await client.get(trends_path(world), params={"from": "2026-10-05", "to": "2026-10-01"})
    too_long = await client.get(trends_path(world), params={"from": "2025-01-01", "to": "2026-10-01"})
    bad_grouping = await client.get(trends_path(world), params={"groupBy": "week"})

    assert (reversed_range.status_code, reversed_range.json()["code"]) == (422, "INVALID_REQUEST")
    assert (too_long.status_code, too_long.json()["code"]) == (422, "INVALID_REQUEST")
    assert bad_grouping.status_code == 422

from datetime import UTC, datetime, time, timedelta

from httpx import AsyncClient

from app.container import Container
from app.modules.insights import DailySnapshotJobHandler
from app.modules.runs import ResultStatus
from app.shared.events import LiveEventType
from app.shared.typing.enums import JobName, QueueName
from tests.api.insights.insight_steps import seed_case, seed_story, sign_in_world
from tests.api.insights.trend_steps import backdate_project, seed_any_run, seed_iteration_result
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_the_snapshot_writes_yesterday_and_backfills_missing_days(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    today = datetime.now(UTC).date()
    yesterday = today - timedelta(days=1)
    world = await sign_in_world(client, container, recording_mailer)
    await backdate_project(container, world, datetime.combine(today - timedelta(days=3), time(8), tzinfo=UTC))
    story = await seed_story(container, world)
    seeded_case = await seed_case(container, world, story)
    yesterday_noon = datetime.combine(yesterday, time(12), tzinfo=UTC)
    run_id = await seed_any_run(container, world, (seeded_case,), yesterday_noon, story=story)
    await seed_iteration_result(container, world, run_id, seeded_case, ResultStatus.PASSED, yesterday_noon)

    await container.snapshot_daily_stats.execute(today)

    async with container.database.begin():
        stored = await container.daily_stats_repository.list_between(
            world.project.id, today - timedelta(days=10), today
        )
    assert [day_stats.day for day_stats in stored] == [today - timedelta(days=3), today - timedelta(days=2), yesterday]
    assert stored[-1].runs_by_executor == {"claude": 1}
    assert stored[-1].passed_count == 1
    assert stored[0].passed_count == 0
    assert any(
        event.type is LiveEventType.INSIGHTS_CHANGED and event.project_id == world.project.id
        for event in recording_live_event_publisher.events
    )


async def test_a_second_snapshot_recomputes_yesterday_without_duplicates(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    today = datetime.now(UTC).date()
    yesterday = today - timedelta(days=1)
    world = await sign_in_world(client, container, recording_mailer)
    await backdate_project(container, world, datetime.combine(yesterday, time(1), tzinfo=UTC))
    story = await seed_story(container, world)
    seeded_case = await seed_case(container, world, story)
    other_case = await seed_case(container, world, story)
    yesterday_noon = datetime.combine(yesterday, time(12), tzinfo=UTC)
    run_id = await seed_any_run(container, world, (seeded_case, other_case), yesterday_noon, story=story)
    await seed_iteration_result(container, world, run_id, seeded_case, ResultStatus.PASSED, yesterday_noon)
    await container.snapshot_daily_stats.execute(today)
    await seed_iteration_result(container, world, run_id, other_case, ResultStatus.FAILED, yesterday_noon)

    await container.snapshot_daily_stats.execute(today)

    async with container.database.begin():
        stored = await container.daily_stats_repository.list_between(world.project.id, yesterday, today)
    assert [(day_stats.day, day_stats.passed_count, day_stats.failed_count) for day_stats in stored] == [
        (yesterday, 1, 1)
    ]


async def test_a_project_created_today_gets_no_snapshot(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    today = datetime.now(UTC).date()
    world = await sign_in_world(client, container, recording_mailer)

    await container.snapshot_daily_stats.execute(today)

    async with container.database.begin():
        stored = await container.daily_stats_repository.list_between(world.project.id, today - timedelta(days=5), today)
    assert stored == []


async def test_the_snapshot_job_runs_nightly_on_the_maintenance_queue(container: Container) -> None:
    handler = container.job_handlers[QueueName.MAINTENANCE][JobName.INSIGHTS_DAILY_SNAPSHOT]
    schedules = [
        schedule for schedule in container.job_schedules if schedule.job_name is JobName.INSIGHTS_DAILY_SNAPSHOT
    ]

    assert isinstance(handler, DailySnapshotJobHandler)
    assert [(schedule.queue_name, schedule.cron_pattern) for schedule in schedules] == [
        (QueueName.MAINTENANCE, "0 2 * * *")
    ]

from datetime import timedelta
from uuid import UUID, uuid7

from httpx import AsyncClient
from sqlalchemy import insert, select, update

from app.container import Container
from app.modules.runs import ResultStatus
from app.modules.runs.infrastructure import CaseResultTable
from tests.api.plans.plan_steps import (
    create_plan_id,
    read_progress,
    run_story,
    seed_plan,
    set_plan_items,
    sign_off_plan,
    story_item,
    suite_item,
)
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import change_case_status, seed_environment
from tests.api.suites.suite_steps import (
    SuiteWorld,
    find_case_code,
    flag_needs_review,
    raise_story_gap,
    run_suite_with,
    seed_suite,
    seed_suite_world,
)
from tests.conftest import RecordingMailer


def read_cases(progress: dict[str, object]) -> list[dict[str, object]]:
    cases = progress["cases"]
    assert isinstance(cases, list)
    return cases


def read_latest_result(case: dict[str, object]) -> dict[str, object] | None:
    latest_result = case["latestResult"]
    assert latest_result is None or isinstance(latest_result, dict)
    return latest_result


def read_statuses(progress: dict[str, object]) -> list[object]:
    statuses: list[object] = []
    for case in read_cases(progress):
        latest_result = read_latest_result(case)
        statuses.append(None if latest_result is None else latest_result["status"])
    return statuses


def read_first_run_id(progress: dict[str, object]) -> object:
    latest_result = read_latest_result(read_cases(progress)[0])
    assert latest_result is not None
    return latest_result["runId"]


async def seed_world(client: AsyncClient, container: Container, recording_mailer: RecordingMailer) -> SuiteWorld:
    return await seed_suite_world(client, container, recording_mailer)


async def test_the_plan_takes_suite_and_story_cases_once_in_item_order(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world, case_ids=[world.first_story.case_ids[1], world.second_story.case_ids[0]])
    await change_case_status(container, world.first_story.case_ids[0], "deprecated")
    await change_case_status(container, world.second_story.case_ids[1], "draft")
    await flag_needs_review(container, world.second_story.case_ids[0])

    plan_id = await seed_plan(
        client, world, [suite_item(suite_id), story_item(world.first_story), story_item(world.second_story)]
    )

    cases = read_cases(await read_progress(client, world.key, plan_id))
    assert [case["testCaseId"] for case in cases] == [
        str(world.first_story.case_ids[1]),
        str(world.second_story.case_ids[0]),
        str(world.second_story.case_ids[1]),
    ]
    first = cases[0]
    assert first["code"] == await find_case_code(container, world.first_story.case_ids[1])
    assert (first["storyId"], first["storyJiraKey"]) == (str(world.first_story.story_id), world.first_story.jira_key)
    assert (first["status"], first["priority"], first["isNeedingReview"]) == ("ready", "medium", False)
    assert (first["latestResult"], first["activeFailureId"], first["activeFailureStatus"]) == (None, None, None)
    assert cases[1]["isNeedingReview"] is True
    assert cases[2]["status"] == "draft"


async def test_counts_use_each_cases_latest_result_since_the_plan_opened(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    await run_story(client, world, world.first_story, ["passed", "passed"])
    plan_id = await seed_plan(client, world, [story_item(world.first_story), story_item(world.second_story)])

    before = await read_progress(client, world.key, plan_id)
    first_run_id = await run_story(client, world, world.first_story, ["failed", "blocked"])
    await run_story(client, world, world.second_story, ["passed", "skipped"])
    after_first_runs = await read_progress(client, world.key, plan_id)
    rerun_id = await run_story(client, world, world.first_story, ["passed", "skipped"])
    after_rerun = await read_progress(client, world.key, plan_id)

    assert before["counts"] == {"total": 4, "passed": 0, "failed": 0, "blocked": 0, "skipped": 0, "notRun": 4}
    assert read_statuses(after_first_runs) == ["failed", "blocked", "passed", "skipped"]
    assert after_first_runs["counts"] == {
        "total": 4,
        "passed": 1,
        "failed": 1,
        "blocked": 1,
        "skipped": 1,
        "notRun": 0,
    }
    assert read_first_run_id(after_first_runs) == first_run_id
    assert read_statuses(after_rerun) == ["passed", "blocked", "passed", "skipped"]
    assert read_first_run_id(after_rerun) == rerun_id


async def test_suite_runs_count_for_the_plan_too(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    await seed_suite(client, world, case_ids=world.first_story.case_ids)
    plan_id = await seed_plan(client, world, [story_item(world.first_story)])

    run_id = await run_suite_with(client, world, ["passed", "blocked"])

    progress = await read_progress(client, world.key, plan_id)
    assert read_statuses(progress) == ["passed", "blocked"]
    assert read_first_run_id(progress) == run_id


async def test_a_plan_with_an_environment_counts_only_runs_on_it(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    await seed_environment(container, world.project, "Production")
    plan_id = await seed_plan(
        client, world, [story_item(world.first_story)], environmentId=str(world.first_story.environment_id)
    )

    await run_story(client, world, world.first_story, ["passed", "passed"], environment="Production")
    on_production_only = await read_progress(client, world.key, plan_id)
    await run_story(client, world, world.first_story, ["blocked"], environment="Staging")

    assert read_statuses(on_production_only) == [None, None]
    assert read_statuses(await read_progress(client, world.key, plan_id)) == ["blocked", None]


async def test_a_signed_off_plan_keeps_the_results_it_was_signed_off_with(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    plan_id = await seed_plan(client, world, [story_item(world.first_story)])
    await run_story(client, world, world.first_story, ["passed", "passed"])
    use_session(client, world.runner.account.session_token)
    assert (await sign_off_plan(client, world.key, plan_id)).status_code == 200

    await run_story(client, world, world.first_story, ["blocked", "blocked"])

    assert read_statuses(await read_progress(client, world.key, plan_id)) == ["passed", "passed"]


async def test_blockers_list_active_failures_and_open_gaps_of_the_plan(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    plan_id = await seed_plan(client, world, [story_item(world.first_story)])
    await run_story(client, world, world.first_story, ["failed", "passed"])
    await run_story(client, world, world.second_story, ["failed", "passed"])
    gap_id = await raise_story_gap(client, world, world.first_story)
    await raise_story_gap(client, world, world.second_story)

    progress = await read_progress(client, world.key, plan_id)

    failures = progress["failures"]
    gaps = progress["gaps"]
    assert isinstance(failures, list)
    assert isinstance(gaps, list)
    assert [failure["testCaseId"] for failure in failures] == [str(world.first_story.case_ids[0])]
    failure = failures[0]
    assert failure["code"] == await find_case_code(container, world.first_story.case_ids[0])
    assert (failure["storyJiraKey"], failure["status"], failure["assigneeId"]) == (
        world.first_story.jira_key,
        "open",
        None,
    )
    assert read_cases(progress)[0]["activeFailureId"] == failure["failureId"]
    assert read_cases(progress)[0]["activeFailureStatus"] == "open"
    assert [gap["gapId"] for gap in gaps] == [gap_id]
    assert gaps[0]["storyJiraKey"] == world.first_story.jira_key
    assert gaps[0]["question"]
    assert gaps[0]["severity"] == "medium"


async def test_a_story_without_cases_still_brings_its_gaps(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    for case_id in world.first_story.case_ids:
        await change_case_status(container, case_id, "deprecated")
    gap_id = await raise_story_gap(client, world, world.first_story)
    plan_id = await create_plan_id(client, world.key)
    assert (await set_plan_items(client, world.key, plan_id, [story_item(world.first_story)])).status_code == 200

    progress = await read_progress(client, world.key, plan_id)

    assert read_cases(progress) == []
    gaps = progress["gaps"]
    assert isinstance(gaps, list)
    assert [gap["gapId"] for gap in gaps] == [gap_id]


async def add_older_failed_iteration(container: Container, run_id: str, test_case_id: UUID) -> UUID:
    failed_id = uuid7()
    async with container.database.begin():
        session = container.database.get_current_session()
        recorded = await session.scalar(
            select(CaseResultTable).where(
                CaseResultTable.run_id == UUID(run_id), CaseResultTable.test_case_id == test_case_id
            )
        )
        assert recorded is not None
        await session.execute(
            insert(CaseResultTable).values(
                id=failed_id,
                run_id=recorded.run_id,
                test_case_id=recorded.test_case_id,
                test_case_version_id=recorded.test_case_version_id,
                status=ResultStatus.FAILED,
                duration_ms=recorded.duration_ms,
                recorded_by=recorded.recorded_by,
                created_at=recorded.created_at,
                iteration=1,
            )
        )
        await session.execute(
            update(CaseResultTable)
            .where(CaseResultTable.id == recorded.id)
            .values(created_at=recorded.created_at + timedelta(seconds=1))
        )
    return failed_id


async def test_a_data_driven_case_takes_its_worst_iteration_not_its_newest(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    plan_id = await seed_plan(client, world, [story_item(world.first_story)])
    run_id = await run_story(client, world, world.first_story, ["passed", "passed"])
    failed_id = await add_older_failed_iteration(container, run_id, world.first_story.case_ids[0])

    progress = await read_progress(client, world.key, plan_id)

    assert read_statuses(progress) == ["failed", "passed"]
    latest_result = read_latest_result(read_cases(progress)[0])
    assert latest_result is not None
    assert (latest_result["caseResultId"], latest_result["runId"]) == (str(failed_id), run_id)
    assert progress["counts"] == {"total": 2, "passed": 1, "failed": 1, "blocked": 0, "skipped": 0, "notRun": 0}

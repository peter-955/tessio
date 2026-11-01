from datetime import timedelta

from httpx import AsyncClient

from app.container import Container
from app.modules.runs import ResultStatus, RunStatus
from app.modules.test_cases import TestCaseStatus as CaseStatus
from tests.api.insights.insight_steps import (
    BASE_TIME,
    get_ok,
    seed_case,
    seed_result,
    seed_run,
    seed_story,
    sign_in_world,
)
from tests.conftest import RecordingMailer


async def test_lists_latest_result_per_case_including_deprecated(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    first_story = await seed_story(container, world)
    second_story = await seed_story(container, world)
    passed_case = await seed_case(container, world, first_story)
    deprecated_case = await seed_case(container, world, first_story, CaseStatus.DEPRECATED)
    unrun_case = await seed_case(container, world, second_story, CaseStatus.DRAFT)
    first_run = await seed_run(container, world, first_story, (passed_case, deprecated_case), RunStatus.FAILED)
    await seed_result(container, world, first_run, passed_case, ResultStatus.FAILED)
    await seed_result(container, world, first_run, deprecated_case, ResultStatus.BLOCKED)
    rerun_at = BASE_TIME + timedelta(hours=1)
    rerun = await seed_run(container, world, first_story, (passed_case,), RunStatus.PASSED, rerun_at)
    rerun_result_id = await seed_result(container, world, rerun, passed_case, ResultStatus.PASSED, rerun_at)
    url = f"/api/projects/{world.project.key}/case-latest-results"

    all_results = (await get_ok(client, url)).json()
    story_results = (await get_ok(client, url, {"storyKey": first_story.jira_key.lower()})).json()
    unknown_results = (await get_ok(client, url, {"storyKey": "NOPE-1"})).json()

    assert [result["code"] for result in all_results] == [passed_case.code, deprecated_case.code, unrun_case.code]
    assert all_results[0]["caseId"] == str(passed_case.id)
    assert all_results[0]["storyId"] == str(first_story.id)
    assert all_results[0]["latestResult"]["caseResultId"] == str(rerun_result_id)
    assert all_results[0]["latestResult"]["status"] == "passed"
    assert all_results[1]["latestResult"]["status"] == "blocked"
    assert all_results[2]["latestResult"] is None
    assert [result["code"] for result in story_results] == [passed_case.code, deprecated_case.code]
    assert unknown_results == []


async def test_other_project_results_are_not_listed(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    other_world = await sign_in_world(client, container, recording_mailer)
    other_story = await seed_story(container, other_world)
    await seed_case(container, other_world, other_story)
    world = await sign_in_world(client, container, recording_mailer)

    response = await get_ok(client, f"/api/projects/{world.project.key}/case-latest-results")

    assert response.json() == []

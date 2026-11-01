from datetime import timedelta
from uuid import uuid7

from httpx import AsyncClient

from app.container import Container
from app.modules.runs import ResultStatus
from app.modules.stories import SprintState
from app.modules.stories import TestStatus as StoryTestStatus
from tests.api.insights.insight_steps import (
    BASE_TIME,
    InsightWorld,
    get_ok,
    seed_case,
    seed_failure,
    seed_gap,
    seed_result,
    seed_run,
    seed_sprint,
    seed_story,
    sign_in_world,
)
from tests.conftest import RecordingMailer

ZERO_COVERAGE = {
    "criterionCount": 0,
    "coveredCount": 0,
    "passedCount": 0,
    "failedCount": 0,
    "blockedCount": 0,
    "notRunCount": 0,
    "uncoveredCount": 0,
}


async def get_dashboard(client: AsyncClient, world: InsightWorld, sprint_id: str | None = None) -> dict[str, object]:
    params = None if sprint_id is None else {"sprintId": sprint_id}
    body: dict[str, object] = (await get_ok(client, f"/api/projects/{world.project.key}/dashboard", params)).json()
    return body


def read_sprint_id(body: dict[str, object]) -> object:
    sprint = body["sprint"]
    assert isinstance(sprint, dict)
    return sprint["id"]


async def test_dashboard_summarises_the_latest_active_sprint(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    old_sprint_id = await seed_sprint(container, world, SprintState.ACTIVE, BASE_TIME)
    sprint_id = await seed_sprint(container, world, SprintState.ACTIVE, BASE_TIME + timedelta(days=7))
    await seed_sprint(container, world, SprintState.ACTIVE, None)
    await seed_sprint(container, world, SprintState.FUTURE, BASE_TIME + timedelta(days=30))
    first_story = await seed_story(container, world, sprint_id, ("AC1", "AC2"))
    second_story = await seed_story(container, world, sprint_id, ("AC1",), test_status=StoryTestStatus.IN_TEST)
    await seed_story(container, world, sprint_id, test_status=StoryTestStatus.PASSED)
    missing_story = await seed_story(container, world, sprint_id, ("AC1",), True, StoryTestStatus.IN_TEST)
    old_story = await seed_story(container, world, old_sprint_id, ("AC1",), test_status=StoryTestStatus.FAILED)
    passing_case = await seed_case(container, world, first_story, criterion_codes=("AC1",))
    run_id = await seed_run(container, world, first_story, (passing_case,))
    await seed_result(container, world, run_id, passing_case, ResultStatus.PASSED)
    failing_case = await seed_case(container, world, second_story, criterion_codes=("AC1",))
    await seed_failure(container, world, failing_case)
    await seed_failure(container, world, await seed_case(container, world, missing_story, criterion_codes=("AC1",)))
    await seed_failure(container, world, await seed_case(container, world, old_story, criterion_codes=("AC1",)))
    await seed_gap(container, world, first_story)
    await seed_gap(container, world, missing_story)
    await seed_gap(container, world, old_story)

    body = await get_dashboard(client, world)

    sprint = body["sprint"]
    assert isinstance(sprint, dict)
    assert sprint["id"] == str(sprint_id)
    assert sprint["state"] == "active"
    assert sprint["startAt"] == (BASE_TIME + timedelta(days=7)).isoformat().replace("+00:00", "Z")
    assert body["storyCount"] == 3
    assert body["testStatusCounts"] == {"notStarted": 1, "readyForTest": 0, "inTest": 1, "passed": 1, "failed": 0}
    assert body["openGapCount"] == 1
    assert body["activeFailureCount"] == 1
    assert body["coverage"] == {
        "criterionCount": 3,
        "coveredCount": 2,
        "passedCount": 1,
        "failedCount": 1,
        "blockedCount": 0,
        "notRunCount": 0,
        "uncoveredCount": 1,
    }


async def test_same_start_prefers_higher_jira_sprint_id_and_explicit_sprint_wins(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    await seed_sprint(container, world, SprintState.ACTIVE, BASE_TIME, jira_sprint_id=9)
    lower_sprint_id = await seed_sprint(container, world, SprintState.ACTIVE, BASE_TIME, jira_sprint_id=5)
    higher_sprint_id = await seed_sprint(container, world, SprintState.ACTIVE, BASE_TIME, jira_sprint_id=12)
    closed_sprint_id = await seed_sprint(container, world, SprintState.CLOSED, BASE_TIME, jira_sprint_id=2)
    await seed_story(container, world, closed_sprint_id, test_status=StoryTestStatus.PASSED)

    default_body = await get_dashboard(client, world)
    lower_body = await get_dashboard(client, world, str(lower_sprint_id))
    closed_body = await get_dashboard(client, world, str(closed_sprint_id))

    assert read_sprint_id(default_body) == str(higher_sprint_id)
    assert read_sprint_id(lower_body) == str(lower_sprint_id)
    assert read_sprint_id(closed_body) == str(closed_sprint_id)
    assert closed_body["storyCount"] == 1
    assert closed_body["testStatusCounts"] == {
        "notStarted": 0,
        "readyForTest": 0,
        "inTest": 0,
        "passed": 1,
        "failed": 0,
    }


async def test_no_active_sprint_gives_empty_summary(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    future_sprint_id = await seed_sprint(container, world, SprintState.FUTURE, BASE_TIME)
    story = await seed_story(container, world, future_sprint_id, ("AC1",))
    await seed_gap(container, world, story)

    body = await get_dashboard(client, world)

    assert body == {
        "sprint": None,
        "storyCount": 0,
        "testStatusCounts": {"notStarted": 0, "readyForTest": 0, "inTest": 0, "passed": 0, "failed": 0},
        "openGapCount": 0,
        "activeFailureCount": 0,
        "coverage": ZERO_COVERAGE,
    }


async def test_unknown_sprint_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)

    response = await client.get(f"/api/projects/{world.project.key}/dashboard", params={"sprintId": str(uuid7())})

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"

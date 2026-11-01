from datetime import timedelta
from uuid import uuid7

from httpx import AsyncClient

from app.container import Container
from app.modules.failures.typing.enums import FailureStatus
from app.modules.gaps.typing.enums import GapStatus
from app.modules.runs import ResultStatus, RunStatus
from app.modules.stories import SprintState
from app.modules.test_cases import TestCaseStatus as CaseStatus
from tests.api.insights.insight_steps import (
    BASE_TIME,
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


async def test_progress_counts_coverage_gaps_failures_and_last_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    sprint_id = await seed_sprint(container, world, SprintState.ACTIVE, BASE_TIME)
    story = await seed_story(container, world, sprint_id, ("AC1", "AC2", "AC3"))
    quiet_story = await seed_story(container, world, None, ("AC1",), is_missing=True)
    passing_case = await seed_case(container, world, story, criterion_codes=("AC1",))
    failing_case = await seed_case(container, world, story, criterion_codes=("AC2",))
    verified_case = await seed_case(container, world, story, CaseStatus.DRAFT)
    fixed_case = await seed_case(container, world, story, CaseStatus.DRAFT)
    await seed_failure(container, world, failing_case, FailureStatus.OPEN, created_at=BASE_TIME)
    await seed_failure(container, world, fixed_case, FailureStatus.FIXED, created_at=BASE_TIME)
    await seed_failure(container, world, verified_case, FailureStatus.VERIFIED, created_at=BASE_TIME)
    await seed_gap(container, world, story)
    await seed_gap(container, world, story)
    await seed_gap(container, world, story, status=GapStatus.RESOLVED)
    last_run_at = BASE_TIME + timedelta(days=1)
    last_run_id = await seed_run(container, world, story, (passing_case,), RunStatus.RUNNING, last_run_at)
    await seed_result(container, world, last_run_id, passing_case, ResultStatus.PASSED, last_run_at)
    url = f"/api/projects/{world.project.key}/story-progress"

    all_progress = (await get_ok(client, url)).json()
    sprint_progress = (await get_ok(client, url, {"sprintId": str(sprint_id)})).json()

    progress_by_key = {progress["jiraKey"]: progress for progress in all_progress}
    assert set(progress_by_key) == {story.jira_key, quiet_story.jira_key}
    story_progress = progress_by_key[story.jira_key]
    assert story_progress["storyId"] == str(story.id)
    assert story_progress["coverage"] == {
        "criterionCount": 3,
        "coveredCount": 2,
        "passedCount": 1,
        "failedCount": 1,
        "blockedCount": 0,
        "notRunCount": 0,
        "uncoveredCount": 1,
    }
    assert story_progress["openGapCount"] == 2
    assert story_progress["activeFailureCount"] == 2
    assert story_progress["lastRun"] == {
        "id": str(last_run_id),
        "status": "running",
        "startedAt": last_run_at.isoformat().replace("+00:00", "Z"),
        "finishedAt": None,
    }
    quiet_progress = progress_by_key[quiet_story.jira_key]
    assert quiet_progress["coverage"]["criterionCount"] == 1
    assert quiet_progress["coverage"]["uncoveredCount"] == 1
    assert quiet_progress["openGapCount"] == 0
    assert quiet_progress["activeFailureCount"] == 0
    assert quiet_progress["lastRun"] is None
    assert [progress["jiraKey"] for progress in sprint_progress] == [story.jira_key]


async def test_unknown_sprint_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    other_world = await sign_in_world(client, container, recording_mailer)
    other_sprint_id = await seed_sprint(container, other_world, SprintState.ACTIVE, BASE_TIME)
    world = await sign_in_world(client, container, recording_mailer)
    url = f"/api/projects/{world.project.key}/story-progress"

    unknown_response = await client.get(url, params={"sprintId": str(uuid7())})
    foreign_response = await client.get(url, params={"sprintId": str(other_sprint_id)})

    assert unknown_response.status_code == 404
    assert unknown_response.json()["message"] == "Sprint not found."
    assert foreign_response.status_code == 404

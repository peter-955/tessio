from datetime import timedelta
from uuid import uuid7

from httpx import AsyncClient

from app.container import Container
from app.modules.runs import ResultStatus, RunStatus
from app.modules.test_cases import TestCaseStatus as CaseStatus
from tests.api.insights.insight_steps import (
    BASE_TIME,
    InsightWorld,
    SeededStory,
    get_ok,
    remove_criterion,
    seed_case,
    seed_result,
    seed_run,
    seed_story,
    sign_in_world,
)
from tests.conftest import RecordingMailer

LATER = BASE_TIME + timedelta(hours=1)
LATEST = BASE_TIME + timedelta(hours=2)


async def get_traceability(client: AsyncClient, world: InsightWorld, story: SeededStory) -> dict[str, object]:
    response = await get_ok(client, f"/api/projects/{world.project.key}/stories/{story.jira_key}/traceability")
    body: dict[str, object] = response.json()
    return body


def read_statuses(body: dict[str, object]) -> dict[str, str]:
    criteria = body["criteria"]
    assert isinstance(criteria, list)
    return {criterion["code"]: criterion["status"] for criterion in criteria}


def read_case(body: dict[str, object], code: str) -> dict[str, object]:
    cases = body["cases"]
    assert isinstance(cases, list)
    matching: dict[str, object] = next(case for case in cases if case["code"] == code)
    return matching


async def test_matrix_lists_criteria_cases_links_and_coverage(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world, criterion_codes=("AC1", "AC2", "AC3", "AC4"))
    await remove_criterion(container, story.criterion_ids["AC2"])
    ready_case = await seed_case(container, world, story, criterion_codes=("AC1", "AC2"), is_needing_review=True)
    draft_case = await seed_case(container, world, story, CaseStatus.DRAFT, ("AC1", "AC4"))
    deprecated_case = await seed_case(container, world, story, CaseStatus.DEPRECATED, ("AC3",))
    run_id = await seed_run(container, world, story, (ready_case,))
    result_id = await seed_result(container, world, run_id, ready_case, ResultStatus.PASSED)

    body = await get_traceability(client, world, story)

    assert body["storyId"] == str(story.id)
    assert body["jiraKey"] == story.jira_key
    assert body["coverage"] == {
        "criterionCount": 3,
        "coveredCount": 2,
        "passedCount": 1,
        "failedCount": 0,
        "blockedCount": 0,
        "notRunCount": 1,
        "uncoveredCount": 1,
    }
    criteria = body["criteria"]
    assert isinstance(criteria, list)
    assert [criterion["code"] for criterion in criteria] == ["AC1", "AC3", "AC4", "AC2"]
    assert [criterion["removedAt"] is None for criterion in criteria] == [True, True, True, False]
    assert read_statuses(body) == {"AC1": "passed", "AC3": "uncovered", "AC4": "not_run", "AC2": "passed"}
    assert criteria[0]["linkedCaseIds"] == [str(ready_case.id), str(draft_case.id)]
    assert criteria[1]["linkedCaseIds"] == []
    cases = body["cases"]
    assert isinstance(cases, list)
    assert [case["code"] for case in cases] == [ready_case.code, draft_case.code]
    assert str(deprecated_case.id) not in {case["id"] for case in cases}
    first_case = read_case(body, ready_case.code)
    assert first_case["needsReview"] is True
    assert first_case["status"] == "ready"
    assert first_case["priority"] == "medium"
    criterion_ids = first_case["criterionIds"]
    assert isinstance(criterion_ids, list)
    assert sorted(criterion_ids) == sorted([str(story.criterion_ids["AC1"]), str(story.criterion_ids["AC2"])])
    assert first_case["latestResult"] == {
        "caseResultId": str(result_id),
        "runId": str(run_id),
        "status": "passed",
        "recordedAt": BASE_TIME.isoformat().replace("+00:00", "Z"),
        "testCaseVersionId": str(ready_case.version_id),
    }
    assert read_case(body, draft_case.code)["latestResult"] is None


async def test_rerun_pass_replaces_failure(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world, criterion_codes=("AC1",))
    case = await seed_case(container, world, story, criterion_codes=("AC1",))
    first_run = await seed_run(container, world, story, (case,), RunStatus.FAILED, BASE_TIME)
    await seed_result(container, world, first_run, case, ResultStatus.FAILED, BASE_TIME)
    rerun = await seed_run(container, world, story, (case,), RunStatus.PASSED, LATER)
    await seed_result(container, world, rerun, case, ResultStatus.PASSED, LATER)

    body = await get_traceability(client, world, story)

    assert read_statuses(body) == {"AC1": "passed"}


async def test_later_run_without_the_case_keeps_the_failure(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world, criterion_codes=("AC1", "AC2"))
    failing_case = await seed_case(container, world, story, criterion_codes=("AC1",))
    other_case = await seed_case(container, world, story, criterion_codes=("AC2",))
    first_run = await seed_run(container, world, story, (failing_case, other_case), RunStatus.FAILED, BASE_TIME)
    await seed_result(container, world, first_run, failing_case, ResultStatus.FAILED, BASE_TIME)
    await seed_result(container, world, first_run, other_case, ResultStatus.BLOCKED, BASE_TIME)
    later_run = await seed_run(container, world, story, (other_case,), RunStatus.RUNNING, LATER)
    await seed_result(container, world, later_run, other_case, ResultStatus.PASSED, LATER)

    body = await get_traceability(client, world, story)

    assert read_statuses(body) == {"AC1": "failed", "AC2": "passed"}
    latest_result = read_case(body, failing_case.code)["latestResult"]
    assert isinstance(latest_result, dict)
    assert latest_result["runId"] == str(first_run)


async def test_newer_skipped_result_keeps_the_failure(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world, criterion_codes=("AC1",))
    case = await seed_case(container, world, story, criterion_codes=("AC1",))
    first_run = await seed_run(container, world, story, (case,), RunStatus.FAILED, BASE_TIME)
    await seed_result(container, world, first_run, case, ResultStatus.FAILED, BASE_TIME)
    later_run = await seed_run(container, world, story, (case,), RunStatus.ABORTED, LATER)
    await seed_result(container, world, later_run, case, ResultStatus.SKIPPED, LATER)

    body = await get_traceability(client, world, story)

    assert read_statuses(body) == {"AC1": "failed"}
    latest_result = read_case(body, case.code)["latestResult"]
    assert isinstance(latest_result, dict)
    assert latest_result["status"] == "failed"


async def test_only_skipped_result_is_latest_and_criterion_not_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world, criterion_codes=("AC1",))
    case = await seed_case(container, world, story, criterion_codes=("AC1",))
    run_id = await seed_run(container, world, story, (case,))
    await seed_result(container, world, run_id, case, ResultStatus.SKIPPED)

    body = await get_traceability(client, world, story)

    assert read_statuses(body) == {"AC1": "not_run"}
    latest_result = read_case(body, case.code)["latestResult"]
    assert isinstance(latest_result, dict)
    assert latest_result["status"] == "skipped"


async def test_same_recorded_time_is_broken_by_higher_id(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world, criterion_codes=("AC1",))
    case = await seed_case(container, world, story, criterion_codes=("AC1",))
    lower_id = uuid7()
    higher_id = uuid7()
    first_run = await seed_run(container, world, story, (case,), RunStatus.FAILED, BASE_TIME)
    second_run = await seed_run(container, world, story, (case,), RunStatus.PASSED, LATER)
    await seed_result(container, world, second_run, case, ResultStatus.FAILED, LATEST, higher_id)
    await seed_result(container, world, first_run, case, ResultStatus.PASSED, LATEST, lower_id)

    body = await get_traceability(client, world, story)

    latest_result = read_case(body, case.code)["latestResult"]
    assert isinstance(latest_result, dict)
    assert latest_result["caseResultId"] == str(higher_id)
    assert read_statuses(body) == {"AC1": "failed"}


async def test_story_key_is_matched_case_insensitively(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)
    story = await seed_story(container, world, criterion_codes=("AC1",))

    response = await client.get(f"/api/projects/{world.project.key}/stories/{story.jira_key.lower()}/traceability")

    assert response.status_code == 200, response.text
    assert response.json()["storyId"] == str(story.id)


async def test_unknown_story_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer)

    response = await client.get(f"/api/projects/{world.project.key}/stories/NOPE-1/traceability")

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"

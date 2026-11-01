from httpx import AsyncClient

from app.container import Container
from app.modules.stories import TestStatus as StoryTestStatus
from app.modules.test_cases import TestCaseStatus as CaseStatus
from app.shared.events import LiveEventType
from tests.api.runs.manual.manual_run_steps import (
    STEP_COUNT,
    find_story_test_status,
    seed_manual_run_project,
    start_manual_run,
    start_manual_run_id,
)
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_manual_run_starts_with_fixed_case_versions(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)

    response = await start_manual_run(client, seeded)

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["executor"] == "manual"
    assert body["status"] == "running"
    assert body["storyId"] == str(seeded.story_id)
    assert body["environmentId"] == str(seeded.environment_id)
    assert body["startedBy"] == str(seeded.qc.user_id)
    assert body["parentRunId"] is None
    assert body["finishedAt"] is None
    assert [case["testCaseId"] for case in body["cases"]] == [str(case.id) for case in seeded.cases]
    assert [case["testCaseVersionId"] for case in body["cases"]] == [str(case.version_id) for case in seeded.cases]
    first_case = body["cases"][0]
    assert first_case["title"] == "Case 1"
    assert first_case["resultStatus"] is None
    assert first_case["steps"][0] == {"order": 1, "action": "Action 1", "expected": "Expected 1"}
    assert len(first_case["steps"]) == STEP_COUNT
    assert await find_story_test_status(container, seeded.story_id) is StoryTestStatus.IN_TEST
    started_events = [
        event for event in recording_live_event_publisher.events if event.type is LiveEventType.RUN_STARTED
    ]
    assert started_events[-1].ids == {"runId": body["id"], "storyId": str(seeded.story_id)}
    assert started_events[-1].project_id == seeded.project.id
    assert any(event.type is LiveEventType.STORY_CHANGED for event in recording_live_event_publisher.events)


async def test_manual_run_can_pick_cases(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)

    response = await start_manual_run(client, seeded, testCaseIds=[str(seeded.cases[1].id)])

    assert response.status_code == 201, response.text
    assert [case["testCaseId"] for case in response.json()["cases"]] == [str(seeded.cases[1].id)]


async def test_open_gap_blocks_manual_run(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    gap_response = await client.post(
        f"/api/projects/{seeded.key}/stories/{seeded.story_key}/gaps",
        json={"type": "missing_ac", "question": "Which currencies are accepted?"},
    )
    assert gap_response.status_code == 201, gap_response.text

    response = await start_manual_run(client, seeded)

    assert response.status_code == 409
    assert response.json()["code"] == "OPEN_GAPS_BLOCK_RUN"


async def test_second_run_on_story_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)
    await start_manual_run_id(client, seeded)

    response = await start_manual_run(client, seeded)

    assert response.status_code == 409
    assert response.json()["code"] == "RUN_ALREADY_RUNNING"


async def test_draft_case_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer, (CaseStatus.READY, CaseStatus.DRAFT))

    response = await start_manual_run(client, seeded, testCaseIds=[str(seeded.cases[1].id)])

    assert response.status_code == 409
    assert response.json()["code"] == "CASE_NOT_READY"


async def test_story_without_ready_cases_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer, (CaseStatus.DRAFT,))

    response = await start_manual_run(client, seeded)

    assert response.status_code == 409
    assert response.json()["code"] == "NO_READY_CASES"


async def test_unknown_story_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    seeded = await seed_manual_run_project(client, container, recording_mailer)

    response = await client.post(f"/api/projects/{seeded.key}/runs", json={"storyKey": "NOPE-1"})

    assert response.status_code == 404

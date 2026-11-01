from datetime import timedelta

import pytest
from httpx import AsyncClient

from app.container import Container
from app.modules.failures.typing.enums import FailureStatus
from app.modules.gaps.typing.enums import GapSeverity, GapStatus
from app.modules.stories import SprintState
from app.modules.test_cases import TestCaseStatus as CaseStatus
from app.shared.permissions import ProjectRole
from tests.api.insights.insight_steps import (
    BASE_TIME,
    InsightWorld,
    get_ok,
    remove_criterion,
    seed_case,
    seed_failure,
    seed_gap,
    seed_sprint,
    seed_story,
    sign_in_world,
)
from tests.api.projects.user_steps import create_invited_user
from tests.conftest import RecordingMailer


async def get_my_work(client: AsyncClient, world: InsightWorld) -> dict[str, object]:
    body: dict[str, object] = (await get_ok(client, f"/api/projects/{world.project.key}/my-work")).json()
    return body


def read_list(body: dict[str, object], name: str) -> dict[str, object]:
    section = body[name]
    assert isinstance(section, dict)
    return section


def read_items(body: dict[str, object], name: str, key: str) -> list[object]:
    items = read_list(body, name)["items"]
    assert isinstance(items, list)
    return [item[key] for item in items]


@pytest.mark.parametrize(
    ("role", "sections"),
    [
        (ProjectRole.ADMIN, ["cases_to_write", "failures_to_fix", "gaps_to_answer"]),
        (ProjectRole.QC, ["cases_to_write", "gaps_to_answer"]),
        (ProjectRole.DEV, ["failures_to_fix", "gaps_to_answer"]),
        (ProjectRole.BA, ["gaps_to_answer"]),
        (ProjectRole.PM, ["gaps_to_answer"]),
        (ProjectRole.VIEWER, []),
    ],
)
async def test_sections_follow_the_role(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    role: ProjectRole,
    sections: list[str],
) -> None:
    world = await sign_in_world(client, container, recording_mailer, role)
    sprint_id = await seed_sprint(container, world, SprintState.ACTIVE, BASE_TIME)
    story = await seed_story(container, world, sprint_id, ("AC1",))
    own_case = await seed_case(container, world, story, CaseStatus.DRAFT)
    await seed_failure(container, world, own_case, FailureStatus.OPEN, world.user_id)
    await seed_gap(container, world, story, assignee_id=world.user_id)
    unassigned_case = await seed_case(container, world, story)
    await seed_failure(container, world, unassigned_case, FailureStatus.REOPENED)

    body = await get_my_work(client, world)

    assert body["role"] == role.value
    assert body["sections"] == sections
    assert read_list(body, "uncoveredCriteria")["totalCount"] == (1 if "cases_to_write" in sections else 0)
    assert read_list(body, "draftCases")["totalCount"] == (1 if "cases_to_write" in sections else 0)
    assert read_list(body, "failuresToFix")["totalCount"] == (1 if "failures_to_fix" in sections else 0)
    assert read_list(body, "gapsToAnswer")["totalCount"] == (1 if "gaps_to_answer" in sections else 0)
    assert body["unassignedFailureCount"] == 1
    sprint = body["sprint"]
    assert isinstance(sprint, dict)
    assert sprint["id"] == str(sprint_id)


async def test_qc_sees_own_draft_cases_and_uncovered_criteria_of_the_sprint(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer, ProjectRole.QC)
    other_user_id = await create_invited_user(container, recording_mailer)
    sprint_id = await seed_sprint(container, world, SprintState.ACTIVE, BASE_TIME)
    other_sprint_id = await seed_sprint(container, world, SprintState.CLOSED, BASE_TIME - timedelta(days=30))
    story = await seed_story(container, world, sprint_id, ("AC1", "AC2", "AC3", "AC4"))
    await remove_criterion(container, story.criterion_ids["AC4"])
    missing_story = await seed_story(container, world, sprint_id, ("AC1",), is_missing=True)
    other_story = await seed_story(container, world, other_sprint_id, ("AC1",))
    draft_case = await seed_case(container, world, story, CaseStatus.DRAFT, ("AC2",), created_at=BASE_TIME)
    review_case = await seed_case(
        container, world, other_story, CaseStatus.IN_REVIEW, created_at=BASE_TIME + timedelta(hours=1)
    )
    await seed_case(container, world, story, CaseStatus.READY)
    await seed_case(container, world, story, CaseStatus.DEPRECATED, ("AC3",))
    await seed_case(container, world, missing_story, CaseStatus.DRAFT, created_by=other_user_id)

    body = await get_my_work(client, world)

    uncovered = read_list(body, "uncoveredCriteria")
    assert uncovered["totalCount"] == 2
    assert uncovered["items"] == [
        {
            "criterionId": str(story.criterion_ids["AC1"]),
            "code": "AC1",
            "text": "Criterion AC1",
            "storyJiraKey": story.jira_key,
            "storyTitle": story.title,
        },
        {
            "criterionId": str(story.criterion_ids["AC3"]),
            "code": "AC3",
            "text": "Criterion AC3",
            "storyJiraKey": story.jira_key,
            "storyTitle": story.title,
        },
    ]
    drafts = read_list(body, "draftCases")
    assert drafts["totalCount"] == 2
    assert drafts["items"] == [
        {
            "caseId": str(review_case.id),
            "code": review_case.code,
            "title": f"Case {review_case.number}",
            "status": "in_review",
            "storyJiraKey": other_story.jira_key,
        },
        {
            "caseId": str(draft_case.id),
            "code": draft_case.code,
            "title": f"Case {draft_case.number}",
            "status": "draft",
            "storyJiraKey": story.jira_key,
        },
    ]


async def test_dev_sees_own_failures_to_fix_oldest_first(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer, ProjectRole.DEV)
    other_user_id = await create_invited_user(container, recording_mailer)
    story = await seed_story(container, world)
    statuses = [
        (FailureStatus.REOPENED, world.user_id, BASE_TIME + timedelta(hours=2)),
        (FailureStatus.OPEN, world.user_id, BASE_TIME),
        (FailureStatus.FIXED, world.user_id, BASE_TIME),
        (FailureStatus.VERIFIED, world.user_id, BASE_TIME),
        (FailureStatus.OPEN, other_user_id, BASE_TIME),
        (FailureStatus.OPEN, None, BASE_TIME),
        (FailureStatus.FIXED, None, BASE_TIME),
    ]
    failure_ids = []
    for status, assignee_id, created_at in statuses:
        seeded_case = await seed_case(container, world, story)
        failure_ids.append(await seed_failure(container, world, seeded_case, status, assignee_id, created_at))

    body = await get_my_work(client, world)

    failures = read_list(body, "failuresToFix")
    assert failures["totalCount"] == 2
    assert read_items(body, "failuresToFix", "failureId") == [str(failure_ids[1]), str(failure_ids[0])]
    first_item = read_items(body, "failuresToFix", "status")
    assert first_item == ["open", "reopened"]
    items = failures["items"]
    assert isinstance(items, list)
    assert items[0]["caseCode"] == "TC-2"
    assert items[0]["caseTitle"] == "Case 2"
    assert items[0]["storyJiraKey"] == story.jira_key
    assert items[0]["openedAt"] == BASE_TIME.isoformat().replace("+00:00", "Z")
    assert body["unassignedFailureCount"] == 1


async def test_gaps_come_from_own_and_role_queue_by_severity(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer, ProjectRole.BA)
    other_user_id = await create_invited_user(container, recording_mailer)
    story = await seed_story(container, world)
    low_id = await seed_gap(container, world, story, world.user_id, severity=GapSeverity.LOW, created_at=BASE_TIME)
    high_late_id = await seed_gap(
        container,
        world,
        story,
        None,
        ProjectRole.BA,
        severity=GapSeverity.HIGH,
        created_at=BASE_TIME + timedelta(hours=2),
    )
    high_early_id = await seed_gap(
        container,
        world,
        story,
        world.user_id,
        ProjectRole.BA,
        severity=GapSeverity.HIGH,
        created_at=BASE_TIME + timedelta(hours=1),
    )
    medium_id = await seed_gap(container, world, story, None, ProjectRole.BA, created_at=BASE_TIME)
    await seed_gap(container, world, story, other_user_id, ProjectRole.BA)
    await seed_gap(container, world, story, None, ProjectRole.QC)
    await seed_gap(container, world, story, world.user_id, status=GapStatus.RESOLVED)

    body = await get_my_work(client, world)

    assert read_list(body, "gapsToAnswer")["totalCount"] == 4
    assert read_items(body, "gapsToAnswer", "gapId") == [
        str(high_early_id),
        str(high_late_id),
        str(medium_id),
        str(low_id),
    ]
    assert read_items(body, "gapsToAnswer", "storyJiraKey") == [story.jira_key] * 4
    assert read_items(body, "gapsToAnswer", "type") == ["missing_step"] * 4


async def test_lists_are_capped_with_total_count(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await sign_in_world(client, container, recording_mailer, ProjectRole.QC)
    story = await seed_story(container, world)
    case_ids = []
    for index in range(21):
        seeded_case = await seed_case(
            container, world, story, CaseStatus.DRAFT, created_at=BASE_TIME + timedelta(minutes=index)
        )
        case_ids.append(str(seeded_case.id))

    body = await get_my_work(client, world)

    assert read_list(body, "draftCases")["totalCount"] == 21
    assert read_items(body, "draftCases", "caseId") == list(reversed(case_ids))[:20]
    assert body["sprint"] is None
    assert read_list(body, "uncoveredCriteria") == {"totalCount": 0, "items": []}

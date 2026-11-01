from uuid import UUID

from httpx import AsyncClient

from app.modules.stories import CriteriaChange, SyncJiraProjectJobHandler
from app.shared.events import LiveEventType
from tests.api.stories.story_steps import build_issue, build_sprint, seed_jira_connection, set_board
from tests.api.test_cases.case_steps import (
    CaseProject,
    change_status,
    create_case_code,
    get_case,
    remove_criterion,
    set_up_case_project,
)
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.conftest import RecordingMailer
from tests.fakes.fake_jira_client import FakeJiraClient
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


def build_change(
    case_project: CaseProject,
    added: frozenset[UUID] = frozenset(),
    changed: frozenset[UUID] = frozenset(),
    removed: frozenset[UUID] = frozenset(),
) -> CriteriaChange:
    return CriteriaChange(
        project_id=case_project.project.id,
        story_id=case_project.story.id,
        added_criterion_ids=added,
        changed_criterion_ids=changed,
        removed_criterion_ids=removed,
    )


async def handle(test_cases_container: CasesContainer, change: CriteriaChange) -> None:
    async with test_cases_container.database.begin():
        await test_cases_container.criteria_changed_handler.handle(change)


async def test_changed_and_removed_criteria_flag_linked_cases_except_deprecated_ones(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer, ["A", "B", "C"])
    first_id, second_id, third_id = case_project.story.criterion_ids
    jira_key = case_project.story.jira_key
    both = await create_case_code(client, case_project.key, jira_key, criterionIds=[str(first_id), str(second_id)])
    deprecated = await create_case_code(client, case_project.key, jira_key, criterionIds=[str(first_id)])
    unrelated = await create_case_code(client, case_project.key, jira_key, criterionIds=[str(third_id)])
    await change_status(client, case_project.key, deprecated, "deprecated")
    events_before = len(recording_live_event_publisher.events)

    await handle(test_cases_container, build_change(case_project, changed=frozenset({first_id})))
    await handle(test_cases_container, build_change(case_project, removed=frozenset({second_id})))

    flagged = (await get_case(client, case_project.key, both)).json()
    assert flagged["needsReview"] is True
    assert flagged["needsReviewAt"] is not None
    assert flagged["needsReviewCriterionIds"] == sorted([str(first_id), str(second_id)])
    assert flagged["status"] == "draft"
    assert (await get_case(client, case_project.key, deprecated)).json()["needsReview"] is False
    assert (await get_case(client, case_project.key, unrelated)).json()["needsReview"] is False
    assert recording_live_event_publisher.events[events_before:] == []
    listed = await client.get(f"/api/projects/{case_project.key}/test-cases", params={"needsReview": "true"})
    assert [summary["code"] for summary in listed.json()] == [both]


async def test_added_criteria_flag_nothing(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    first_id, _ = case_project.story.criterion_ids
    code = await create_case_code(client, case_project.key, case_project.story.jira_key, criterionIds=[str(first_id)])

    await handle(test_cases_container, build_change(case_project, added=frozenset({first_id})))

    assert (await get_case(client, case_project.key, code)).json()["needsReview"] is False


async def test_mark_reviewed_clears_the_flag_and_is_idempotent(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    first_id, _ = case_project.story.criterion_ids
    code = await create_case_code(client, case_project.key, case_project.story.jira_key, criterionIds=[str(first_id)])
    await handle(test_cases_container, build_change(case_project, changed=frozenset({first_id})))

    reviewed = await client.post(f"/api/projects/{case_project.key}/test-cases/{code}/review")
    events_after_review = len(recording_live_event_publisher.events)
    again = await client.post(f"/api/projects/{case_project.key}/test-cases/{code}/review")

    assert reviewed.status_code == 200
    body = reviewed.json()
    assert body["needsReview"] is False
    assert body["needsReviewCriterionIds"] == []
    assert body["reviewedBy"] == str(case_project.user_id)
    assert body["status"] == "draft"
    assert recording_live_event_publisher.events[-1].type is LiveEventType.TEST_CASE_CHANGED
    assert again.status_code == 200
    assert again.json()["reviewedAt"] == body["reviewedAt"]
    assert len(recording_live_event_publisher.events) == events_after_review


async def test_the_detail_shows_a_removed_criterion(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    first_id, second_id = case_project.story.criterion_ids
    code = await create_case_code(
        client, case_project.key, case_project.story.jira_key, criterionIds=[str(second_id), str(first_id)]
    )
    await remove_criterion(test_cases_container, second_id)

    detail = (await get_case(client, case_project.key, code)).json()

    assert detail["criteria"] == [
        {"id": str(first_id), "code": "AC1", "text": "Pay by card", "isRemoved": False},
        {"id": str(second_id), "code": "AC2", "text": "Get receipt", "isRemoved": True},
    ]


async def test_a_jira_sync_that_changes_a_criterion_flags_the_linked_case(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    project = case_project.project
    jira_client = test_cases_container.jira_client
    assert isinstance(jira_client, FakeJiraClient)
    await seed_jira_connection(test_cases_container, case_project.user_id)
    jira_key = f"{project.key}-7"
    set_board(jira_client, project, {build_sprint(1): [build_issue(project.key, 7, criteria=["Pay", "Receipt"])]})
    await SyncJiraProjectJobHandler(test_cases_container.sync_jira_project).handle({"projectId": str(project.id)})
    story = (await client.get(f"/api/projects/{project.key}/stories/{jira_key}")).json()
    first_id, second_id = (criterion["id"] for criterion in story["criteria"])
    linked = await create_case_code(client, project.key, jira_key, criterionIds=[first_id])
    untouched = await create_case_code(client, project.key, jira_key, criterionIds=[second_id])

    set_board(jira_client, project, {build_sprint(1): [build_issue(project.key, 7, criteria=["Pay now", "Receipt"])]})
    await SyncJiraProjectJobHandler(test_cases_container.sync_jira_project).handle({"projectId": str(project.id)})

    flagged = (await get_case(client, project.key, linked)).json()
    assert flagged["needsReview"] is True
    assert flagged["needsReviewCriterionIds"] == [first_id]
    assert (await get_case(client, project.key, untouched)).json()["needsReview"] is False

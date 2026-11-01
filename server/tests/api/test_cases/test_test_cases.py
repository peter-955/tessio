import asyncio

from httpx import AsyncClient

from app.modules.test_cases.domains.test_case_content.entity import TestCaseContent as CaseContent
from app.modules.test_cases.typing.enums import TestCasePriority as CasePriority
from app.modules.users import WorkspaceRole
from app.shared.events import LiveEventType
from app.shared.permissions import Actor, ProjectRole
from tests.api.test_cases.case_steps import (
    build_step,
    change_status,
    create_case,
    create_case_code,
    seed_story,
    set_up_case_project,
)
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_data.project_steps import add_member, seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_case_codes_count_up_per_project(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    other_project = await seed_project(test_cases_container)
    await add_member(test_cases_container, other_project, case_project.user_id, ProjectRole.QC)
    other_story = await seed_story(test_cases_container, other_project, f"{other_project.key}-1")

    first = await create_case_code(client, case_project.key, case_project.story.jira_key)
    second = await create_case_code(client, case_project.key, case_project.story.jira_key)
    other = await create_case_code(client, other_project.key, other_story.jira_key)

    assert [first, second, other] == ["TC-1", "TC-2", "TC-1"]


async def test_concurrent_creates_get_distinct_numbers(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    actor = Actor(user_id=case_project.user_id, workspace_role=WorkspaceRole.MEMBER)
    content = CaseContent(
        title="Pay", priority=CasePriority.HIGH, business_value=None, preconditions=None, steps=[], criterion_ids=[]
    )

    details = await asyncio.gather(
        *(
            test_cases_container.create_test_case.execute(actor, case_project.key, case_project.story.jira_key, content)
            for _ in range(5)
        )
    )

    assert {detail.test_case.number for detail in details} == {1, 2, 3, 4, 5}


async def test_create_returns_the_first_version_with_links_and_references(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)

    response = await create_case(
        client,
        case_project.key,
        case_project.story.jira_key.lower(),
        title="Pay with a saved card",
        priority="critical",
        preconditions="Signed in as {{ data.user }}",
        steps=[build_step("Open {{data.base_url}}/cart", "Cart shows {{file.invoice}}"), build_step("Pay")],
        criterionIds=[str(case_project.story.criterion_ids[1]), str(case_project.story.criterion_ids[0])],
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["code"] == "TC-1"
    assert body["status"] == "draft"
    assert body["priority"] == "critical"
    assert body["story"]["jiraKey"] == case_project.story.jira_key
    version = body["currentVersion"]
    assert version["number"] == 1
    assert [step["order"] for step in version["steps"]] == [1, 2]
    assert version["dataKeys"] == ["base_url", "user"]
    assert version["fileVersionIds"] == []
    first_id, second_id = case_project.story.criterion_ids
    assert version["criterionIds"] == [str(second_id), str(first_id)]
    assert [criterion["code"] for criterion in body["criteria"]] == ["AC1", "AC2"]
    assert body["unknownReferences"] == ["data.base_url", "data.user", "file.invoice"]
    assert body["needsReview"] is False


async def test_lookup_by_code_ignores_case_and_unknown_codes_are_not_found(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    await create_case_code(client, case_project.key, case_project.story.jira_key)

    found = await client.get(f"/api/projects/{case_project.key}/test-cases/tc-1")
    missing = await client.get(f"/api/projects/{case_project.key}/test-cases/TC-2")
    malformed = await client.get(f"/api/projects/{case_project.key}/test-cases/TC-01")

    assert found.status_code == 200
    assert found.json()["code"] == "TC-1"
    assert [missing.status_code, malformed.status_code] == [404, 404]
    assert missing.json()["code"] == "NOT_FOUND"


async def test_unknown_story_is_not_found(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)

    response = await create_case(client, case_project.key, f"{case_project.key}-404")

    assert response.status_code == 404
    assert response.json() == {"code": "NOT_FOUND", "message": "Story not found."}


async def test_criterion_of_another_story_cannot_be_linked(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    other_story = await seed_story(test_cases_container, case_project.project, f"{case_project.key}-2", ["Other"])

    response = await create_case(
        client, case_project.key, case_project.story.jira_key, criterionIds=[str(other_story.criterion_ids[0])]
    )

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REQUEST"


async def test_blank_title_or_step_action_is_rejected(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)

    blank_title = await create_case(client, case_project.key, case_project.story.jira_key, title="   ")
    blank_action = await create_case(client, case_project.key, case_project.story.jira_key, steps=[build_step("  ")])
    padded = await create_case(client, case_project.key, f"  {case_project.story.jira_key} ", title="  Pay  ")

    assert (blank_title.status_code, blank_action.status_code) == (422, 422)
    assert padded.status_code == 201
    assert padded.json()["currentVersion"]["title"] == "Pay"


async def test_list_filters_by_story_status_priority_criterion_review_and_query(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    story = case_project.story
    other_story = await seed_story(test_cases_container, case_project.project, f"{case_project.key}-2")
    await create_case_code(
        client, case_project.key, story.jira_key, title="Pay by card", criterionIds=[str(story.criterion_ids[0])]
    )
    await create_case_code(
        client, case_project.key, story.jira_key, title="Refund 100% of_order", priority="high", steps=[build_step("a")]
    )
    await create_case_code(client, case_project.key, other_story.jira_key, title="Download receipt")
    await change_status(client, case_project.key, "TC-2", "in_review")

    async def list_codes(**params: str) -> list[str]:
        response = await client.get(f"/api/projects/{case_project.key}/test-cases", params=params)
        assert response.status_code == 200, response.text
        return [summary["code"] for summary in response.json()]

    assert await list_codes() == ["TC-1", "TC-2", "TC-3"]
    assert await list_codes(storyKey=story.jira_key.lower()) == ["TC-1", "TC-2"]
    assert await list_codes(storyKey=f"{case_project.key}-404") == []
    assert await list_codes(status="in_review") == ["TC-2"]
    assert await list_codes(priority="high") == ["TC-2"]
    assert await list_codes(criterionId=str(story.criterion_ids[0])) == ["TC-1"]
    assert await list_codes(needsReview="false") == ["TC-1", "TC-2", "TC-3"]
    assert await list_codes(needsReview="true") == []
    assert await list_codes(query="TC-2") == ["TC-2"]
    assert await list_codes(query="tc-3") == ["TC-3"]
    assert await list_codes(query="RECEIPT") == ["TC-3"]
    assert await list_codes(query="100%") == ["TC-2"]
    assert await list_codes(query="f_o") == ["TC-2"]


async def test_list_shows_summary_fields(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    criterion_id = str(case_project.story.criterion_ids[0])
    created = await create_case(
        client,
        case_project.key,
        case_project.story.jira_key,
        steps=[build_step("a"), build_step("b")],
        criterionIds=[criterion_id],
    )

    response = await client.get(f"/api/projects/{case_project.key}/test-cases")

    summary = response.json()[0]
    assert summary["id"] == created.json()["id"]
    assert summary["storyKey"] == case_project.story.jira_key
    assert summary["storyId"] == str(case_project.story.id)
    assert summary["currentVersionNumber"] == 1
    assert summary["currentVersionId"] == created.json()["currentVersion"]["id"]
    assert summary["stepCount"] == 2
    assert summary["criterionIds"] == [criterion_id]
    assert summary["needsReview"] is False
    assert summary["lastSavedAt"] == created.json()["currentVersion"]["createdAt"]


async def test_create_publishes_test_case_changed(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)

    body = (await create_case(client, case_project.key, case_project.story.jira_key)).json()

    events = [event for event in recording_live_event_publisher.events if event.type is LiveEventType.TEST_CASE_CHANGED]
    assert len(events) == 1
    assert events[0].project_id == case_project.project.id
    assert events[0].ids == {"testCaseId": body["id"], "code": "TC-1", "storyId": str(case_project.story.id)}

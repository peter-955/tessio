from uuid import uuid7

from httpx import AsyncClient

from app.shared.events import LiveEventType
from tests.api.test_cases.case_steps import build_step, change_status, create_case_code, get_case, update_case
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_cases.review_comment_steps import (
    AUTHOR_NAME,
    REVIEWER_NAME,
    act_as,
    add_comment,
    add_comment_id,
    list_comments,
    resolve_comment,
    set_up_review_project,
)
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_a_comment_is_listed_with_its_author_version_and_step(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    act_as(client, review_project.reviewer)

    created = await add_comment(client, review_project, body="  Step 2 needs the amount.  ", stepOrder=2)
    await add_comment(client, review_project, body="Add a precondition for the signed-in user.")
    comments = await list_comments(client, review_project)

    assert created.status_code == 201, created.text
    current_version_id = (await get_case(client, review_project.key, review_project.case_code)).json()[
        "currentVersion"
    ]["id"]
    body = created.json()
    assert body == {
        "id": body["id"],
        "versionId": current_version_id,
        "versionNumber": 1,
        "stepOrder": 2,
        "body": "Step 2 needs the amount.",
        "authorId": str(review_project.reviewer.user_id),
        "authorName": REVIEWER_NAME,
        "createdAt": body["createdAt"],
        "isResolved": False,
        "resolvedAt": None,
        "resolvedBy": None,
        "resolvedByName": None,
    }
    assert [comment["body"] for comment in comments] == [
        "Step 2 needs the amount.",
        "Add a precondition for the signed-in user.",
    ]
    assert comments[1]["stepOrder"] is None


async def test_a_comment_can_name_an_older_version_and_one_of_its_steps(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    saved = await update_case(client, review_project.key, review_project.case_code, 1, steps=[build_step("Pay")])
    assert saved.status_code == 200, saved.text
    act_as(client, review_project.reviewer)

    on_old_step = await add_comment(client, review_project, versionNumber=1, stepOrder=2)
    on_missing_step = await add_comment(client, review_project, stepOrder=2)
    on_missing_version = await add_comment(client, review_project, versionNumber=9)

    assert on_old_step.status_code == 201, on_old_step.text
    assert on_old_step.json()["versionNumber"] == 1
    assert on_missing_step.status_code == 422
    assert on_missing_step.json() == {"code": "INVALID_REQUEST", "message": "Comment on a step of this version."}
    assert on_missing_version.status_code == 404
    assert on_missing_version.json() == {"code": "NOT_FOUND", "message": "Test case version not found."}


async def test_a_blank_or_too_long_comment_is_refused(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)

    blank = await add_comment(client, review_project, body="   ")
    too_long = await add_comment(client, review_project, body="x" * 5001)
    bad_step = await add_comment(client, review_project, stepOrder=0)

    assert [blank.status_code, too_long.status_code, bad_step.status_code] == [422, 422, 422]
    assert await list_comments(client, review_project) == []


async def test_a_deprecated_case_takes_no_comments(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    await change_status(client, review_project.key, review_project.case_code, "deprecated")

    response = await add_comment(client, review_project)

    assert response.status_code == 409
    assert response.json() == {
        "code": "CONFLICT",
        "message": "Restore the test case to Draft before commenting on it.",
    }


async def test_resolving_records_who_resolved_and_is_idempotent(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    act_as(client, review_project.reviewer)
    comment_id = await add_comment_id(client, review_project)
    act_as(client, review_project.author)
    events_before = len(recording_live_event_publisher.events)

    first = await resolve_comment(client, review_project, comment_id)
    second = await resolve_comment(client, review_project, comment_id)

    assert first.status_code == 200, first.text
    resolved = first.json()
    assert resolved["isResolved"] is True
    assert resolved["resolvedAt"] is not None
    assert resolved["resolvedBy"] == str(review_project.author.user_id)
    assert resolved["resolvedByName"] == AUTHOR_NAME
    assert resolved["authorName"] == REVIEWER_NAME
    assert second.status_code == 200
    assert second.json() == resolved
    assert len(recording_live_event_publisher.events) == events_before + 1


async def test_an_unknown_comment_or_one_of_another_case_is_not_found(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    comment_id = await add_comment_id(client, review_project)
    other_code = await create_case_code(client, review_project.key, review_project.story.jira_key)
    other_path = f"/api/projects/{review_project.key}/test-cases/{other_code}/review-comments"

    unknown = await resolve_comment(client, review_project, str(uuid7()))
    other_case = await client.put(f"{other_path}/{comment_id}/resolve")

    assert unknown.status_code == 404
    assert unknown.json() == {"code": "NOT_FOUND", "message": "Review comment not found."}
    assert other_case.status_code == 404
    assert (await client.get(other_path)).json() == []


async def test_an_open_comment_blocks_ready_until_it_is_resolved(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    act_as(client, review_project.reviewer)
    first_id = await add_comment_id(client, review_project)
    second_id = await add_comment_id(client, review_project, stepOrder=1)
    await resolve_comment(client, review_project, first_id)

    blocked = await change_status(client, review_project.key, review_project.case_code, "ready")
    await resolve_comment(client, review_project, second_id)
    ready = await change_status(client, review_project.key, review_project.case_code, "ready")

    assert blocked.status_code == 409
    assert blocked.json() == {
        "code": "REVIEW_COMMENTS_OPEN",
        "message": "Resolve the open review comments (1) before marking the case Ready.",
    }
    assert ready.status_code == 200, ready.text
    assert ready.json()["status"] == "ready"


async def test_open_comments_block_only_the_move_to_ready(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    act_as(client, review_project.reviewer)
    assert (await change_status(client, review_project.key, review_project.case_code, "ready")).status_code == 200
    await add_comment_id(client, review_project)

    still_ready = await get_case(client, review_project.key, review_project.case_code)
    edited = await update_case(client, review_project.key, review_project.case_code, 1, title="Pay with a card")
    back_to_review = await change_status(client, review_project.key, review_project.case_code, "in_review")
    to_draft = await change_status(client, review_project.key, review_project.case_code, "draft")

    assert still_ready.json()["status"] == "ready"
    assert edited.status_code == 200, edited.text
    assert back_to_review.status_code == 200
    assert to_draft.status_code == 200


async def test_adding_and_resolving_publish_review_comment_changed(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    detail = (await get_case(client, review_project.key, review_project.case_code)).json()
    events_before = len(recording_live_event_publisher.events)

    comment_id = await add_comment_id(client, review_project)
    await resolve_comment(client, review_project, comment_id)

    events = recording_live_event_publisher.events[events_before:]
    assert [event.type for event in events] == [LiveEventType.REVIEW_COMMENT_CHANGED] * 2
    assert {event.project_id for event in events} == {review_project.project.id}
    assert events[0].ids == {
        "testCaseId": detail["id"],
        "code": review_project.case_code,
        "storyId": str(review_project.story.id),
        "commentId": comment_id,
    }

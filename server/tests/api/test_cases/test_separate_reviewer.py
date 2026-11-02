from httpx import AsyncClient

from tests.api.test_cases.case_steps import change_status, get_case, update_case
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_cases.review_comment_steps import (
    act_as,
    flag_needs_review,
    set_require_separate_reviewer,
    set_up_review_project,
)
from tests.conftest import RecordingMailer

REVIEWER_IS_AUTHOR = {
    "code": "REVIEWER_IS_AUTHOR",
    "message": "This project needs a reviewer who did not write the version under review.",
}


async def test_the_author_may_mark_their_own_case_ready_when_the_setting_is_off(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)

    response = await change_status(client, review_project.key, review_project.case_code, "ready")

    assert response.status_code == 200, response.text
    assert response.json()["reviewedBy"] == str(review_project.author.user_id)


async def test_the_setting_refuses_the_author_and_lets_another_reviewer_mark_ready(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    await set_require_separate_reviewer(test_cases_container, review_project.project, True)

    by_author = await change_status(client, review_project.key, review_project.case_code, "ready")
    act_as(client, review_project.reviewer)
    by_reviewer = await change_status(client, review_project.key, review_project.case_code, "ready")

    assert by_author.status_code == 403
    assert by_author.json() == REVIEWER_IS_AUTHOR
    assert by_reviewer.status_code == 200, by_reviewer.text
    assert by_reviewer.json()["reviewedBy"] == str(review_project.reviewer.user_id)


async def test_the_author_is_whoever_saved_the_current_version(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    await set_require_separate_reviewer(test_cases_container, review_project.project, True)
    act_as(client, review_project.reviewer)
    saved = await update_case(client, review_project.key, review_project.case_code, 1, title="Pay with a card")
    assert saved.status_code == 200, saved.text

    by_last_editor = await change_status(client, review_project.key, review_project.case_code, "ready")
    act_as(client, review_project.author)
    by_first_author = await change_status(client, review_project.key, review_project.case_code, "ready")

    assert by_last_editor.status_code == 403
    assert by_last_editor.json() == REVIEWER_IS_AUTHOR
    assert by_first_author.status_code == 200, by_first_author.text


async def test_the_setting_leaves_other_status_moves_to_the_author(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    await set_require_separate_reviewer(test_cases_container, review_project.project, True)

    to_draft = await change_status(client, review_project.key, review_project.case_code, "draft")
    to_review = await change_status(client, review_project.key, review_project.case_code, "in_review")

    assert to_draft.status_code == 200
    assert to_review.status_code == 200


async def test_the_setting_refuses_the_author_marking_their_own_case_reviewed(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    await set_require_separate_reviewer(test_cases_container, review_project.project, True)
    await flag_needs_review(test_cases_container, review_project)
    review_path = f"/api/projects/{review_project.key}/test-cases/{review_project.case_code}/review"

    by_author = await client.post(review_path)
    still_flagged = await get_case(client, review_project.key, review_project.case_code)
    act_as(client, review_project.reviewer)
    by_reviewer = await client.post(review_path)

    assert by_author.status_code == 403
    assert by_author.json() == REVIEWER_IS_AUTHOR
    assert still_flagged.json()["needsReview"] is True
    assert by_reviewer.status_code == 200, by_reviewer.text
    assert by_reviewer.json()["needsReview"] is False


async def test_the_author_marks_their_own_case_reviewed_when_the_setting_is_off(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    review_project = await set_up_review_project(client, test_cases_container, recording_mailer)
    await flag_needs_review(test_cases_container, review_project)

    response = await client.post(f"/api/projects/{review_project.key}/test-cases/{review_project.case_code}/review")

    assert response.status_code == 200, response.text
    assert response.json()["needsReview"] is False

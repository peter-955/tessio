from datetime import UTC, datetime

from httpx import AsyncClient
from sqlalchemy import update

from app.modules.test_cases.infrastructure import TestCaseTable as CaseTable
from app.modules.test_cases.typing.constants import TEST_CASE_STATUS_TRANSITIONS
from app.modules.test_cases.typing.enums import TestCaseStatus as CaseStatus
from tests.api.test_cases.case_steps import (
    build_step,
    change_status,
    create_case,
    create_case_code,
    seed_data_item,
    seed_test_file_upload,
    set_up_case_project,
    update_case,
)
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.api.test_data.environment_steps import create_data_item, create_environment
from tests.api.test_data.project_steps import SeededProject
from tests.conftest import RecordingMailer


async def force_status(container: CasesContainer, project: SeededProject, number: int, status: CaseStatus) -> None:
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(CaseTable)
            .where(CaseTable.project_id == project.id, CaseTable.number == number)
            .values(status=status)
        )


async def test_status_changes_follow_the_transition_table(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    outcomes: dict[tuple[CaseStatus, CaseStatus], int] = {}
    number = 0
    for current in CaseStatus:
        for target in CaseStatus:
            if current is target:
                continue
            number += 1
            await create_case(client, case_project.key, case_project.story.jira_key, steps=[build_step("Pay")])
            await force_status(test_cases_container, case_project.project, number, current)
            response = await change_status(client, case_project.key, f"TC-{number}", target.value)
            outcomes[current, target] = response.status_code
            if response.status_code == 409:
                assert response.json()["code"] == "INVALID_STATUS_TRANSITION"
            else:
                assert response.json()["status"] == target.value

    assert outcomes == {
        (current, target): 200 if target in TEST_CASE_STATUS_TRANSITIONS[current] else 409
        for current in CaseStatus
        for target in CaseStatus
        if current is not target
    }


async def test_the_same_status_is_a_no_op(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    await create_case(client, case_project.key, case_project.story.jira_key)

    response = await change_status(client, case_project.key, "TC-1", "draft")

    assert response.status_code == 200
    assert response.json()["statusChangedAt"] is None


async def test_ready_needs_a_step(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    await create_case(client, case_project.key, case_project.story.jira_key)
    await change_status(client, case_project.key, "TC-1", "in_review")

    response = await change_status(client, case_project.key, "TC-1", "ready")

    assert response.status_code == 409
    assert response.json() == {
        "code": "CASE_NOT_READY",
        "message": "Add at least one step before marking the case Ready.",
    }


async def test_ready_refuses_unknown_data_and_file_references(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    await seed_data_item(test_cases_container, case_project.project, "user")
    await create_case(
        client,
        case_project.key,
        case_project.story.jira_key,
        preconditions="Signed in as {{data.user}}",
        steps=[build_step("Open {{ data.x }}", "Shows {{file.y}}")],
    )
    await change_status(client, case_project.key, "TC-1", "in_review")

    response = await change_status(client, case_project.key, "TC-1", "ready")

    assert response.status_code == 422
    assert response.json() == {"code": "UNKNOWN_REFERENCE", "message": "Unknown references: {{data.x}}, {{file.y}}."}


async def test_an_environment_data_item_and_an_attached_file_satisfy_the_references(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    environment_id = await create_environment(client, case_project.project)
    await create_data_item(client, case_project.project, "x", "value", environment_id=environment_id)
    steps = [build_step("{{data.x}} {{file.y}}")]
    await create_case(client, case_project.key, case_project.story.jira_key, steps=steps)
    file_id = await seed_test_file_upload(test_cases_container, case_project.project, case_project.user_id)
    attached = await client.post(
        f"/api/projects/{case_project.key}/test-cases/TC-1/files",
        json={"key": "y", "fileId": str(file_id), "baseVersionNumber": 1},
    )
    assert attached.json()["unknownReferences"] == []
    await change_status(client, case_project.key, "TC-1", "in_review")

    response = await change_status(client, case_project.key, "TC-1", "ready")

    assert response.status_code == 200, response.text
    assert response.json()["status"] == "ready"


async def test_editing_a_ready_case_keeps_the_ready_rules(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    code = await create_case_code(client, case_project.key, case_project.story.jira_key, steps=[build_step("Pay")])
    await change_status(client, case_project.key, code, "in_review")
    await change_status(client, case_project.key, code, "ready")

    unknown = await update_case(client, case_project.key, code, 1, steps=[build_step("Open {{data.missing}}")])
    no_steps = await update_case(client, case_project.key, code, 1, steps=[])
    allowed = await update_case(client, case_project.key, code, 1, title="Pay by card again")

    assert unknown.status_code == 422
    assert unknown.json()["code"] == "UNKNOWN_REFERENCE"
    assert no_steps.status_code == 409
    assert no_steps.json()["code"] == "CASE_NOT_READY"
    assert allowed.status_code == 200
    assert allowed.json()["status"] == "ready"
    assert allowed.json()["currentVersion"]["number"] == 2


async def test_draft_cases_may_hold_unknown_references(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    await create_case(client, case_project.key, case_project.story.jira_key)

    response = await update_case(client, case_project.key, "TC-1", 1, preconditions="{{file.contract}}")

    assert response.status_code == 200
    assert response.json()["unknownReferences"] == ["file.contract"]


async def test_moving_to_ready_clears_the_review_flag(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    await create_case(client, case_project.key, case_project.story.jira_key, steps=[build_step("Pay")])
    await change_status(client, case_project.key, "TC-1", "in_review")
    async with test_cases_container.database.begin():
        await test_cases_container.database.get_current_session().execute(
            update(CaseTable)
            .where(CaseTable.project_id == case_project.project.id)
            .values(needs_review_at=datetime.now(UTC), needs_review_criterion_ids=case_project.story.criterion_ids)
        )

    response = await change_status(client, case_project.key, "TC-1", "ready")

    body = response.json()
    assert body["needsReview"] is False
    assert body["needsReviewAt"] is None
    assert body["needsReviewCriterionIds"] == []
    assert body["reviewedBy"] == str(case_project.user_id)
    assert body["reviewedAt"] is not None
    assert body["statusChangedAt"] is not None

from httpx import AsyncClient

from app.shared.events import LiveEventType
from tests.api.test_cases.case_steps import (
    build_step,
    change_status,
    create_case,
    get_case,
    remove_criterion,
    set_up_case_project,
    update_case,
)
from tests.api.test_cases.conftest import TestCasesTestContainer as CasesContainer
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def list_versions(client: AsyncClient, project_key: str, case_code: str) -> list[dict[str, object]]:
    response = await client.get(f"/api/projects/{project_key}/test-cases/{case_code}/versions")
    assert response.status_code == 200, response.text
    versions: list[dict[str, object]] = response.json()
    return versions


async def test_patch_adds_a_version_and_keeps_the_old_one(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    created = await create_case(
        client, case_project.key, case_project.story.jira_key, title="Pay", businessValue="Revenue", steps=[]
    )
    first_version = created.json()["currentVersion"]

    response = await update_case(
        client, case_project.key, "TC-1", 1, title="Pay by card", priority="high", steps=[build_step("Open cart")]
    )

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["title"] == "Pay by card"
    assert body["priority"] == "high"
    assert body["status"] == "draft"
    assert body["currentVersion"]["number"] == 2
    assert body["currentVersion"]["businessValue"] == "Revenue"
    versions = await list_versions(client, case_project.key, "TC-1")
    assert [version["number"] for version in versions] == [2, 1]
    assert versions[1] == first_version


async def test_empty_text_clears_business_value_and_preconditions(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    await create_case(client, case_project.key, case_project.story.jira_key, businessValue="Revenue", preconditions="x")

    response = await update_case(client, case_project.key, "TC-1", 1, businessValue="", preconditions=" ")

    version = response.json()["currentVersion"]
    assert [version["businessValue"], version["preconditions"]] == [None, None]


async def test_stale_base_version_is_a_conflict(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    await create_case(client, case_project.key, case_project.story.jira_key)
    await update_case(client, case_project.key, "TC-1", 1, title="Second")

    response = await update_case(client, case_project.key, "TC-1", 1, title="Third")

    assert response.status_code == 409
    assert response.json() == {"code": "CONFLICT", "message": "Someone saved a newer version. Reload and try again."}


async def test_unchanged_patch_adds_no_version_and_no_event(
    client: AsyncClient,
    test_cases_container: CasesContainer,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    await create_case(client, case_project.key, case_project.story.jira_key, steps=[build_step("a", "b")])
    events_before = len(recording_live_event_publisher.events)

    response = await update_case(
        client, case_project.key, "TC-1", 1, title="Pay by card", steps=[build_step("a", "b")], priority="medium"
    )

    assert response.status_code == 200
    assert response.json()["currentVersion"]["number"] == 1
    assert len(await list_versions(client, case_project.key, "TC-1")) == 1
    assert [
        event
        for event in recording_live_event_publisher.events[events_before:]
        if event.type is LiveEventType.TEST_CASE_CHANGED
    ] == []


async def test_patch_replaces_the_criterion_links(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer, ["A", "B", "C"])
    first_id, second_id, third_id = (str(criterion_id) for criterion_id in case_project.story.criterion_ids)
    await create_case(client, case_project.key, case_project.story.jira_key, criterionIds=[first_id, second_id])

    response = await update_case(client, case_project.key, "TC-1", 1, criterionIds=[third_id, second_id, third_id])

    body = response.json()
    assert body["currentVersion"]["criterionIds"] == [third_id, second_id]
    assert [criterion["code"] for criterion in body["criteria"]] == ["AC2", "AC3"]
    listed = await client.get(f"/api/projects/{case_project.key}/test-cases", params={"criterionId": first_id})
    assert listed.json() == []
    listed = await client.get(f"/api/projects/{case_project.key}/test-cases", params={"criterionId": third_id})
    assert [summary["code"] for summary in listed.json()] == ["TC-1"]


async def test_deprecated_case_cannot_be_edited(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    await create_case(client, case_project.key, case_project.story.jira_key)
    await change_status(client, case_project.key, "TC-1", "deprecated")

    response = await update_case(client, case_project.key, "TC-1", 1, title="Changed")

    assert response.status_code == 409
    assert response.json() == {"code": "CONFLICT", "message": "Restore the test case to Draft before editing it."}


async def test_a_removed_criterion_stays_linked_but_cannot_be_newly_linked(
    client: AsyncClient, test_cases_container: CasesContainer, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, test_cases_container, recording_mailer)
    first_id, second_id = case_project.story.criterion_ids
    await create_case(client, case_project.key, case_project.story.jira_key, criterionIds=[str(first_id)])
    await remove_criterion(test_cases_container, first_id)
    await remove_criterion(test_cases_container, second_id)

    kept = await update_case(client, case_project.key, "TC-1", 1, title="Renamed", criterionIds=[str(first_id)])
    refused = await update_case(client, case_project.key, "TC-1", 2, criterionIds=[str(first_id), str(second_id)])

    assert kept.status_code == 200, kept.text
    assert kept.json()["criteria"] == [{"id": str(first_id), "code": "AC1", "text": "Pay by card", "isRemoved": True}]
    assert refused.status_code == 422
    assert refused.json()["code"] == "INVALID_REQUEST"
    assert (await get_case(client, case_project.key, "TC-1")).json()["currentVersion"]["number"] == 2

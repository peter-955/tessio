from httpx import AsyncClient

from app.container import Container
from app.shared.events import LiveEventType
from tests.api.labels.label_steps import create_label_id, list_case_codes, set_case_labels
from tests.api.test_cases.case_steps import (
    build_step,
    create_case_code,
    get_case,
    seed_story,
    set_up_case_project,
    update_case,
)
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_a_cases_labels_are_set_and_replaced(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    smoke_id = await create_label_id(client, case_project.key, "Smoke", color="green")
    checkout_id = await create_label_id(client, case_project.key, "checkout", color="blue")
    regression_id = await create_label_id(client, case_project.key, "Regression")
    code = await create_case_code(client, case_project.key, case_project.story.jira_key)

    first = await set_case_labels(client, case_project.key, code, [smoke_id, checkout_id, smoke_id])
    event = recording_live_event_publisher.events[-1]
    second = await set_case_labels(client, case_project.key, code.lower(), [regression_id, checkout_id])

    assert first.status_code == 200, first.text
    assert first.json() == [
        {"id": checkout_id, "name": "checkout", "color": "blue"},
        {"id": smoke_id, "name": "Smoke", "color": "green"},
    ]
    assert event.type is LiveEventType.TEST_CASE_CHANGED
    assert event.ids["code"] == code
    assert [label["name"] for label in second.json()] == ["checkout", "Regression"]
    case = (await get_case(client, case_project.key, code)).json()
    assert [label["name"] for label in case["labels"]] == ["checkout", "Regression"]
    assert case["currentVersion"]["number"] == 1


async def test_clearing_labels_leaves_none(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    smoke_id = await create_label_id(client, case_project.key, "Smoke")
    code = await create_case_code(client, case_project.key, case_project.story.jira_key)
    await set_case_labels(client, case_project.key, code, [smoke_id])

    response = await set_case_labels(client, case_project.key, code, [])

    assert response.status_code == 200, response.text
    assert response.json() == []
    assert (await get_case(client, case_project.key, code)).json()["labels"] == []


async def test_setting_the_same_labels_publishes_nothing(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    smoke_id = await create_label_id(client, case_project.key, "Smoke")
    code = await create_case_code(client, case_project.key, case_project.story.jira_key)
    await set_case_labels(client, case_project.key, code, [smoke_id])
    event_count = len(recording_live_event_publisher.events)

    response = await set_case_labels(client, case_project.key, code, [smoke_id])

    assert response.status_code == 200, response.text
    assert len(recording_live_event_publisher.events) == event_count


async def test_labels_survive_a_new_case_version(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    smoke_id = await create_label_id(client, case_project.key, "Smoke")
    code = await create_case_code(client, case_project.key, case_project.story.jira_key)
    await set_case_labels(client, case_project.key, code, [smoke_id])

    response = await update_case(client, case_project.key, code, 1, title="Pay by card again")

    assert response.status_code == 200, response.text
    assert response.json()["currentVersion"]["number"] == 2
    assert [label["name"] for label in response.json()["labels"]] == ["Smoke"]


async def test_a_label_of_another_project_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    other_project = await set_up_case_project(client, container, recording_mailer)
    other_label_id = await create_label_id(client, other_project.key, "Smoke")
    case_project = await set_up_case_project(client, container, recording_mailer)
    own_label_id = await create_label_id(client, case_project.key, "Smoke")
    code = await create_case_code(client, case_project.key, case_project.story.jira_key)

    response = await set_case_labels(client, case_project.key, code, [own_label_id, other_label_id])

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REQUEST"
    assert (await get_case(client, case_project.key, code)).json()["labels"] == []


async def test_an_unknown_case_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)

    response = await set_case_labels(client, case_project.key, "TC-99", [])

    assert response.status_code == 404
    assert response.json()["code"] == "NOT_FOUND"


async def test_a_case_takes_at_most_twenty_labels(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    label_ids = [await create_label_id(client, case_project.key, f"Label {index}") for index in range(21)]
    code = await create_case_code(client, case_project.key, case_project.story.jira_key)

    too_many = await set_case_labels(client, case_project.key, code, label_ids)
    most = await set_case_labels(client, case_project.key, code, label_ids[:20])

    assert too_many.status_code == 422
    assert most.status_code == 200, most.text
    assert len(most.json()) == 20


async def test_the_case_list_shows_labels_and_filters_by_label_name(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    smoke_id = await create_label_id(client, case_project.key, "Smoke", color="green")
    checkout_id = await create_label_id(client, case_project.key, "Checkout")
    await create_label_id(client, case_project.key, "Unused")
    story_key = case_project.story.jira_key
    both_code = await create_case_code(client, case_project.key, story_key, title="Both")
    smoke_code = await create_case_code(client, case_project.key, story_key, title="Smoke only")
    plain_code = await create_case_code(client, case_project.key, story_key, title="Plain")
    await set_case_labels(client, case_project.key, both_code, [smoke_id, checkout_id])
    await set_case_labels(client, case_project.key, smoke_code, [smoke_id])

    response = await client.get(f"/api/projects/{case_project.key}/test-cases")

    labels_by_code = {case["code"]: [label["name"] for label in case["labels"]] for case in response.json()}
    assert labels_by_code == {both_code: ["Checkout", "Smoke"], smoke_code: ["Smoke"], plain_code: []}
    assert await list_case_codes(client, case_project.key, ["smoke"]) == [both_code, smoke_code]
    assert await list_case_codes(client, case_project.key, [" SMOKE ", "checkout"]) == [both_code]
    assert await list_case_codes(client, case_project.key, ["Unused"]) == []
    assert await list_case_codes(client, case_project.key, ["missing"]) == []


async def test_the_label_filter_combines_with_other_filters(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    smoke_id = await create_label_id(client, case_project.key, "Smoke")
    other_story = await seed_story(container, case_project.project, f"{case_project.key}-2")
    first_code = await create_case_code(
        client, case_project.key, case_project.story.jira_key, steps=[build_step("Pay")], priority="high"
    )
    second_code = await create_case_code(client, case_project.key, other_story.jira_key, priority="high")
    await set_case_labels(client, case_project.key, first_code, [smoke_id])
    await set_case_labels(client, case_project.key, second_code, [smoke_id])

    response = await client.get(
        f"/api/projects/{case_project.key}/test-cases",
        params={"label": "Smoke", "storyKey": other_story.jira_key, "priority": "high"},
    )

    assert [case["code"] for case in response.json()] == [second_code]


async def test_the_filter_does_not_match_labels_of_another_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    other_project = await set_up_case_project(client, container, recording_mailer)
    other_label_id = await create_label_id(client, other_project.key, "Smoke")
    other_code = await create_case_code(client, other_project.key, other_project.story.jira_key)
    await set_case_labels(client, other_project.key, other_code, [other_label_id])
    case_project = await set_up_case_project(client, container, recording_mailer)
    await create_case_code(client, case_project.key, case_project.story.jira_key)

    assert await list_case_codes(client, case_project.key, ["Smoke"]) == []

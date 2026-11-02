from httpx import AsyncClient

from app.container import Container
from app.shared.events import LiveEventType
from tests.api.labels.label_steps import (
    create_label,
    create_label_id,
    delete_label,
    list_labels,
    set_case_labels,
    update_label,
)
from tests.api.test_cases.case_steps import create_case_code, get_case, set_up_case_project
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_a_label_is_created_with_a_name_and_a_colour(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)

    response = await create_label(client, case_project.key, "  Smoke  ", color="green")

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "Smoke"
    assert body["color"] == "green"
    assert body["caseCount"] == 0
    assert set(body) == {"id", "name", "color", "caseCount", "createdAt"}
    event = recording_live_event_publisher.events[-1]
    assert event.type is LiveEventType.LABEL_CHANGED
    assert event.project_id == case_project.project.id
    assert event.ids == {"labelId": body["id"]}


async def test_a_label_starts_gray_when_no_colour_is_given(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)

    response = await create_label(client, case_project.key, "Checkout")

    assert response.json()["color"] == "gray"


async def test_label_names_are_unique_in_a_project_without_case(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    await create_label_id(client, case_project.key, "Smoke")

    response = await create_label(client, case_project.key, "SMOKE")

    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICT"


async def test_the_same_name_is_allowed_in_another_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    first = await set_up_case_project(client, container, recording_mailer)
    await create_label_id(client, first.key, "Smoke")
    second = await set_up_case_project(client, container, recording_mailer)

    response = await create_label(client, second.key, "Smoke")

    assert response.status_code == 201, response.text
    assert [label["name"] for label in await list_labels(client, second.key)] == ["Smoke"]


async def test_invalid_names_and_colours_are_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)

    responses = [
        await create_label(client, case_project.key, "   "),
        await create_label(client, case_project.key, "x" * 41),
        await create_label(client, case_project.key, "Smoke", color="#ff0000"),
    ]

    assert [response.status_code for response in responses] == [422, 422, 422]
    assert await list_labels(client, case_project.key) == []


async def test_labels_are_listed_by_name_with_their_case_count(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    smoke_id = await create_label_id(client, case_project.key, "smoke")
    await create_label_id(client, case_project.key, "Checkout")
    regression_id = await create_label_id(client, case_project.key, "Regression")
    story_key = case_project.story.jira_key
    for title in ("First", "Second"):
        code = await create_case_code(client, case_project.key, story_key, title=title)
        assert (await set_case_labels(client, case_project.key, code, [smoke_id])).status_code == 200
    third_code = await create_case_code(client, case_project.key, story_key, title="Third")
    await set_case_labels(client, case_project.key, third_code, [regression_id])

    labels = await list_labels(client, case_project.key)

    assert [(label["name"], label["caseCount"]) for label in labels] == [
        ("Checkout", 0),
        ("Regression", 1),
        ("smoke", 2),
    ]


async def test_a_label_is_renamed_and_recoloured(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    label_id = await create_label_id(client, case_project.key, "Smoke")
    code = await create_case_code(client, case_project.key, case_project.story.jira_key)
    await set_case_labels(client, case_project.key, code, [label_id])
    event_count = len(recording_live_event_publisher.events)

    renamed = await update_label(client, case_project.key, label_id, name="Smoke test")
    recoloured = await update_label(client, case_project.key, label_id, color="red")

    assert renamed.status_code == 200, renamed.text
    assert recoloured.json()["name"] == "Smoke test"
    assert recoloured.json()["color"] == "red"
    assert recoloured.json()["caseCount"] == 1
    new_events = recording_live_event_publisher.events[event_count:]
    assert [event.type for event in new_events] == [LiveEventType.LABEL_CHANGED] * 2
    case = (await get_case(client, case_project.key, code)).json()
    assert case["labels"] == [{"id": label_id, "name": "Smoke test", "color": "red"}]


async def test_an_update_without_a_change_publishes_nothing(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    label_id = await create_label_id(client, case_project.key, "Smoke", color="blue")
    event_count = len(recording_live_event_publisher.events)

    response = await update_label(client, case_project.key, label_id, name="Smoke", color="blue")

    assert response.status_code == 200, response.text
    assert len(recording_live_event_publisher.events) == event_count


async def test_a_rename_to_another_labels_name_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    await create_label_id(client, case_project.key, "Smoke")
    label_id = await create_label_id(client, case_project.key, "Checkout")

    conflict = await update_label(client, case_project.key, label_id, name="smoke")
    own_case_change = await update_label(client, case_project.key, label_id, name="CHECKOUT")

    assert conflict.status_code == 409
    assert conflict.json()["code"] == "CONFLICT"
    assert own_case_change.status_code == 200, own_case_change.text
    assert own_case_change.json()["name"] == "CHECKOUT"


async def test_deleting_a_label_removes_it_from_its_cases(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    smoke_id = await create_label_id(client, case_project.key, "Smoke")
    checkout_id = await create_label_id(client, case_project.key, "Checkout")
    code = await create_case_code(client, case_project.key, case_project.story.jira_key)
    await set_case_labels(client, case_project.key, code, [smoke_id, checkout_id])

    response = await delete_label(client, case_project.key, smoke_id)

    assert response.status_code == 204, response.text
    assert recording_live_event_publisher.events[-1].type is LiveEventType.LABEL_CHANGED
    assert recording_live_event_publisher.events[-1].ids == {"labelId": smoke_id}
    assert [label["name"] for label in await list_labels(client, case_project.key)] == ["Checkout"]
    case = (await get_case(client, case_project.key, code)).json()
    assert [label["name"] for label in case["labels"]] == ["Checkout"]


async def test_an_unknown_label_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    case_project = await set_up_case_project(client, container, recording_mailer)
    unknown_id = "0190f3a0-0000-7000-8000-000000000000"

    responses = [
        await update_label(client, case_project.key, unknown_id, name="Smoke"),
        await delete_label(client, case_project.key, unknown_id),
    ]

    assert [response.status_code for response in responses] == [404, 404]
    assert {response.json()["code"] for response in responses} == {"NOT_FOUND"}

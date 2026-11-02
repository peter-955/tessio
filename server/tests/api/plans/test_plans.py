from uuid import uuid7

import pytest
from httpx import AsyncClient

from app.container import Container
from app.shared.events import LiveEventType
from tests.api.plans.plan_steps import (
    DEFAULT_PLAN_NAME,
    close_plan,
    create_plan,
    create_plan_id,
    plan_path,
    plans_path,
    read_plan,
    seed_plan,
    set_plan_items,
    sign_off_plan,
    story_item,
    suite_item,
)
from tests.api.projects.user_steps import use_session
from tests.api.runs.run_steps import change_case_status, seed_environment, seed_runnable_story
from tests.api.suites.suite_steps import SuiteWorld, archive_suite, seed_suite, seed_suite_world
from tests.api.test_data.project_steps import seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


def list_plan_events(publisher: RecordingLiveEventPublisher, event_type: LiveEventType) -> list[dict[str, str]]:
    return [event.ids for event in publisher.events if event.type is event_type]


async def test_a_plan_is_created_open_and_empty(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    recording_live_event_publisher.events.clear()

    response = await create_plan(
        client,
        world.key,
        "  Release 2.4  ",
        description="Everything for the June release",
        targetDate="2026-12-01",
        environmentId=str(world.first_story.environment_id),
    )

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "Release 2.4"
    assert body["description"] == "Everything for the June release"
    assert body["status"] == "open"
    assert body["targetDate"] == "2026-12-01"
    assert body["environmentId"] == str(world.first_story.environment_id)
    assert body["environmentName"] == "Staging"
    assert body["createdBy"] == str(world.runner.account.user_id)
    assert body["createdByName"] == "Quinn Runner"
    assert (body["signedOffAt"], body["signedOffBy"], body["closedAt"], body["closedBy"]) == (None, None, None, None)
    assert body["items"] == []
    assert body["progress"] == {
        "counts": {"total": 0, "passed": 0, "failed": 0, "blocked": 0, "skipped": 0, "notRun": 0},
        "cases": [],
        "failures": [],
        "gaps": [],
    }
    assert list_plan_events(recording_live_event_publisher, LiveEventType.PLAN_CHANGED) == [{"planId": body["id"]}]


async def test_the_list_shows_plans_newest_first_and_filters_by_status(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    first_id = await seed_plan(client, world, [story_item(world.first_story)], name="First")
    second_id = await create_plan_id(client, world.key, "Second")
    assert (await close_plan(client, world.key, second_id)).status_code == 200

    listed = (await client.get(plans_path(world.key))).json()
    open_only = (await client.get(plans_path(world.key), params={"status": "open"})).json()

    assert [(plan["name"], plan["status"], plan["itemCount"]) for plan in listed] == [
        ("Second", "closed", 0),
        ("First", "open", 1),
    ]
    assert listed[1]["counts"] == {"total": 2, "passed": 0, "failed": 0, "blocked": 0, "skipped": 0, "notRun": 2}
    assert [plan["id"] for plan in open_only] == [first_id]


async def test_a_plan_is_edited_and_only_real_changes_publish(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    plan_id = await create_plan_id(
        client,
        world.key,
        description="Old",
        targetDate="2026-12-01",
        environmentId=str(world.first_story.environment_id),
    )
    recording_live_event_publisher.events.clear()

    renamed = await client.patch(plan_path(world.key, plan_id), json={"name": "Release 2.5", "description": None})
    cleared = await client.patch(plan_path(world.key, plan_id), json={"targetDate": None, "environmentId": None})
    unchanged = await client.patch(plan_path(world.key, plan_id), json={"name": "Release 2.5"})

    assert renamed.status_code == 200, renamed.text
    assert (renamed.json()["name"], renamed.json()["description"]) == ("Release 2.5", None)
    assert renamed.json()["targetDate"] == "2026-12-01"
    assert (cleared.json()["targetDate"], cleared.json()["environmentId"], cleared.json()["environmentName"]) == (
        None,
        None,
        None,
    )
    assert unchanged.status_code == 200
    assert list_plan_events(recording_live_event_publisher, LiveEventType.PLAN_CHANGED) == [{"planId": plan_id}] * 2


async def test_the_environment_must_be_an_active_one_of_the_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    other_project = await seed_project(container)
    foreign_environment_id = await seed_environment(container, other_project)
    archived_environment_id = await seed_environment(container, world.project, "Old", is_archived=True)
    plan_id = await create_plan_id(client, world.key)

    foreign = await create_plan(client, world.key, environmentId=str(foreign_environment_id))
    archived = await client.patch(plan_path(world.key, plan_id), json={"environmentId": str(archived_environment_id)})

    assert (foreign.status_code, foreign.json()["code"]) == (422, "UNKNOWN_REFERENCE")
    assert (archived.status_code, archived.json()["code"]) == (422, "UNKNOWN_REFERENCE")


async def test_items_keep_their_order_and_show_suites_and_stories(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world, case_ids=world.first_story.case_ids)
    await change_case_status(container, world.second_story.case_ids[1], "deprecated")
    plan_id = await create_plan_id(client, world.key)
    recording_live_event_publisher.events.clear()

    response = await set_plan_items(client, world.key, plan_id, [story_item(world.second_story), suite_item(suite_id)])

    assert response.status_code == 200, response.text
    items = response.json()["items"]
    assert [(item["position"], item["kind"]) for item in items] == [(1, "story"), (2, "suite")]
    assert items[0]["storyId"] == str(world.second_story.story_id)
    assert items[0]["storyJiraKey"] == world.second_story.jira_key
    assert items[0]["suiteId"] is None
    assert items[0]["caseCount"] == 1
    assert (items[1]["suiteId"], items[1]["name"], items[1]["caseCount"]) == (suite_id, "Checkout regression", 2)
    assert items[1]["archivedAt"] is None
    assert list_plan_events(recording_live_event_publisher, LiveEventType.PLAN_CHANGED) == [{"planId": plan_id}]
    emptied = await set_plan_items(client, world.key, plan_id, [])
    assert emptied.json()["items"] == []


async def test_an_archived_suite_stays_in_a_plan(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    assert (await archive_suite(client, world.key, suite_id)).status_code == 200

    plan_id = await seed_plan(client, world, [suite_item(suite_id)])

    item = (await read_plan(client, world.key, plan_id))["items"]
    assert isinstance(item, list)
    assert item[0]["archivedAt"] is not None


async def test_items_must_be_unique_single_and_of_this_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)
    other_project = await seed_project(container)
    foreign_story = await seed_runnable_story(container, other_project, world.runner.account.user_id, 1)
    plan_id = await create_plan_id(client, world.key)

    duplicate_story = await set_plan_items(
        client, world.key, plan_id, [story_item(world.first_story), story_item(world.first_story)]
    )
    duplicate_suite = await set_plan_items(client, world.key, plan_id, [suite_item(suite_id), suite_item(suite_id)])
    foreign = await set_plan_items(client, world.key, plan_id, [story_item(foreign_story)])
    unknown_suite = await set_plan_items(client, world.key, plan_id, [suite_item(str(uuid7()))])
    both = await set_plan_items(
        client, world.key, plan_id, [{"suiteId": suite_id, "storyId": str(world.first_story.story_id)}]
    )
    neither = await set_plan_items(client, world.key, plan_id, [{}])

    assert (duplicate_story.status_code, duplicate_story.json()["code"]) == (422, "INVALID_REQUEST")
    assert (duplicate_suite.status_code, duplicate_suite.json()["code"]) == (422, "INVALID_REQUEST")
    assert (foreign.status_code, foreign.json()["code"]) == (422, "UNKNOWN_REFERENCE")
    assert (unknown_suite.status_code, unknown_suite.json()["code"]) == (422, "UNKNOWN_REFERENCE")
    assert [both.status_code, neither.status_code] == [422, 422]
    assert (await read_plan(client, world.key, plan_id))["items"] == []


async def test_another_projects_plan_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    other_world = await seed_suite_world(client, container, recording_mailer)
    other_plan_id = await create_plan_id(client, other_world.key)
    await seed_plan(client, world, [])

    response = await client.get(plan_path(world.key, other_plan_id))

    assert (response.status_code, response.json()["code"]) == (404, "NOT_FOUND")


def build_foreign_plan_write(route: str, world: SuiteWorld, plan_id: str) -> tuple[str, str, dict[str, object] | None]:
    url = plan_path(world.key, plan_id)
    writes: dict[str, tuple[str, str, dict[str, object] | None]] = {
        "update": ("PATCH", url, {"name": "Taken over"}),
        "set_items": ("PUT", f"{url}/items", {"items": [story_item(world.first_story)]}),
        "sign_off": ("POST", f"{url}/sign-off", None),
        "close": ("POST", f"{url}/close", None),
    }
    return writes[route]


@pytest.mark.parametrize("route", ["update", "set_items", "sign_off", "close"])
async def test_another_projects_plan_is_not_found_on_every_write(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, route: str
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    other_world = await seed_suite_world(client, container, recording_mailer)
    other_plan_id = await seed_plan(client, other_world, [story_item(other_world.first_story)])
    use_session(client, world.runner.account.session_token)
    method, url, body = build_foreign_plan_write(route, world, other_plan_id)

    response = await client.request(method, url, json=body)

    assert (response.status_code, response.json()["code"]) == (404, "NOT_FOUND")
    use_session(client, other_world.runner.account.session_token)
    other_plan = await read_plan(client, other_world.key, other_plan_id)
    assert (other_plan["name"], other_plan["status"]) == (DEFAULT_PLAN_NAME, "open")
    items = other_plan["items"]
    assert isinstance(items, list)
    assert [item["storyId"] for item in items] == [str(other_world.first_story.story_id)]


async def test_a_signed_off_plan_can_be_closed_but_no_longer_edited(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    plan_id = await seed_plan(client, world, [story_item(world.first_story)])
    assert (await sign_off_plan(client, world.key, plan_id)).status_code == 200

    refused = [
        await client.patch(plan_path(world.key, plan_id), json={"name": "Late"}),
        await set_plan_items(client, world.key, plan_id, []),
        await sign_off_plan(client, world.key, plan_id),
    ]
    closed = await close_plan(client, world.key, plan_id)
    closed_again = await close_plan(client, world.key, plan_id)

    assert [(response.status_code, response.json()["code"]) for response in refused] == [(409, "PLAN_NOT_OPEN")] * 3
    assert closed.status_code == 200, closed.text
    body = closed.json()
    assert body["status"] == "closed"
    assert body["closedBy"] == str(world.runner.account.user_id)
    assert body["closedByName"] == "Quinn Runner"
    assert body["signedOffAt"] is not None
    assert (closed_again.status_code, closed_again.json()["code"]) == (409, "PLAN_NOT_OPEN")
    assert body["name"] == DEFAULT_PLAN_NAME


async def test_an_open_plan_can_be_closed_without_sign_off(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_suite_world(client, container, recording_mailer)
    plan_id = await seed_plan(client, world, [story_item(world.first_story)])
    recording_live_event_publisher.events.clear()

    closed = await close_plan(client, world.key, plan_id)
    refused = [
        await sign_off_plan(client, world.key, plan_id),
        await set_plan_items(client, world.key, plan_id, []),
    ]

    assert (closed.json()["status"], closed.json()["signedOffAt"]) == ("closed", None)
    assert [(response.status_code, response.json()["code"]) for response in refused] == [(409, "PLAN_NOT_OPEN")] * 2
    assert list_plan_events(recording_live_event_publisher, LiveEventType.PLAN_CHANGED) == [{"planId": plan_id}]
    assert list_plan_events(recording_live_event_publisher, LiveEventType.PLAN_SIGNED_OFF) == []

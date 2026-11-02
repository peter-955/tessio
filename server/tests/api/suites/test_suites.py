import pytest
from httpx import AsyncClient
from sqlalchemy import update

from app.container import Container
from app.modules.stories import SprintState
from app.modules.stories.infrastructure import StoryTable
from app.shared.events import LiveEventType
from app.shared.permissions import ProjectRole
from tests.api.insights.insight_steps import InsightWorld, seed_sprint
from tests.api.labels.label_steps import create_label_id, delete_label, set_case_labels
from tests.api.runs.run_steps import change_case_status, seed_runnable_story
from tests.api.suites.suite_steps import (
    DEFAULT_SUITE_NAME,
    SuiteWorld,
    add_cases_by_filter,
    archive_suite,
    create_suite,
    create_suite_id,
    find_case_code,
    flag_needs_review,
    get_suite,
    seed_suite,
    seed_suite_world,
    set_priority,
    set_suite_cases,
)
from tests.api.test_data.project_steps import add_member, seed_project
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def seed_world(client: AsyncClient, container: Container, recording_mailer: RecordingMailer) -> SuiteWorld:
    return await seed_suite_world(client, container, recording_mailer)


async def test_a_suite_is_created_empty_and_listed(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_world(client, container, recording_mailer)
    recording_live_event_publisher.events.clear()

    response = await create_suite(client, world.key, "  Smoke  ", description="Every release")

    assert response.status_code == 201, response.text
    body = response.json()
    assert body["name"] == "Smoke"
    assert body["description"] == "Every release"
    assert body["cases"] == []
    assert (body["caseCount"], body["readyCaseCount"]) == (0, 0)
    assert body["archivedAt"] is None
    assert body["lastRun"] is None
    assert body["runningRun"] is None
    assert body["createdBy"] == str(world.runner.account.user_id)
    events = [event for event in recording_live_event_publisher.events if event.type is LiveEventType.SUITE_CHANGED]
    assert [event.ids for event in events] == [{"suiteId": body["id"]}]
    listed = (await client.get(f"/api/projects/{world.key}/suites")).json()
    assert [(suite["name"], suite["caseCount"], suite["lastRun"]) for suite in listed] == [("Smoke", 0, None)]


async def test_suite_names_are_unique_without_case_among_active_suites(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    suite_id = await create_suite_id(client, world.key, "Smoke")

    duplicate = await create_suite(client, world.key, "SMOKE")

    assert duplicate.status_code == 409
    assert duplicate.json()["code"] == "SUITE_NAME_ALREADY_USED"
    assert (await archive_suite(client, world.key, suite_id)).status_code == 200
    reused = await create_suite(client, world.key, "smoke")
    assert reused.status_code == 201, reused.text


async def test_cases_keep_the_order_they_are_put_in(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    suite_id = await create_suite_id(client, world.key)
    ordered_ids = [world.case_ids[3], world.case_ids[0], world.case_ids[2]]

    response = await set_suite_cases(client, world.key, suite_id, ordered_ids)

    assert response.status_code == 200, response.text
    cases = response.json()["cases"]
    assert [case["testCaseId"] for case in cases] == [str(case_id) for case_id in ordered_ids]
    assert [case["position"] for case in cases] == [1, 2, 3]
    assert cases[0]["storyJiraKey"] == world.second_story.jira_key
    assert cases[1]["storyJiraKey"] == world.first_story.jira_key
    assert cases[0]["code"] == await find_case_code(container, ordered_ids[0])
    reordered = await set_suite_cases(client, world.key, suite_id, [world.case_ids[0]])
    assert [case["testCaseId"] for case in reordered.json()["cases"]] == [str(world.case_ids[0])]


async def test_putting_the_same_cases_in_the_same_order_changes_nothing(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_world(client, container, recording_mailer)
    suite_id = await create_suite_id(client, world.key)
    ordered_ids = [world.case_ids[1], world.case_ids[0]]
    assert (await set_suite_cases(client, world.key, suite_id, ordered_ids)).status_code == 200
    recording_live_event_publisher.events.clear()

    unchanged = await set_suite_cases(client, world.key, suite_id, ordered_ids)
    unchanged_events = list(recording_live_event_publisher.events)
    reordered = await set_suite_cases(client, world.key, suite_id, list(reversed(ordered_ids)))

    assert unchanged.status_code == 200, unchanged.text
    assert [case["testCaseId"] for case in unchanged.json()["cases"]] == [str(case_id) for case_id in ordered_ids]
    assert [event.type for event in unchanged_events if event.type is LiveEventType.SUITE_CHANGED] == []
    assert reordered.status_code == 200, reordered.text
    changed = [event for event in recording_live_event_publisher.events if event.type is LiveEventType.SUITE_CHANGED]
    assert len(changed) == 1


async def test_cases_must_be_unique_and_of_this_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    suite_id = await create_suite_id(client, world.key)
    other_project = await seed_project(container)
    foreign_story = await seed_runnable_story(container, other_project, world.runner.account.user_id, 1)

    duplicate = await set_suite_cases(client, world.key, suite_id, [world.case_ids[0], world.case_ids[0]])
    foreign = await set_suite_cases(client, world.key, suite_id, [world.case_ids[0], foreign_story.case_ids[0]])

    assert (duplicate.status_code, duplicate.json()["code"]) == (422, "INVALID_REQUEST")
    assert (foreign.status_code, foreign.json()["code"]) == (422, "UNKNOWN_REFERENCE")
    assert (await get_suite(client, world.key, suite_id)).json()["cases"] == []


async def test_ready_count_leaves_out_draft_and_needs_review_cases(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    await change_case_status(container, world.case_ids[1], "draft")
    await flag_needs_review(container, world.case_ids[2])

    suite_id = await seed_suite(client, world)

    detail = (await get_suite(client, world.key, suite_id)).json()
    assert (detail["caseCount"], detail["readyCaseCount"]) == (4, 2)
    assert [case["isRunnable"] for case in detail["cases"]] == [True, False, False, True]
    assert detail["cases"][2]["isNeedingReview"] is True
    listed = (await client.get(f"/api/projects/{world.key}/suites")).json()
    assert (listed[0]["caseCount"], listed[0]["readyCaseCount"]) == (4, 2)


async def test_rename_and_clear_the_description(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_world(client, container, recording_mailer)
    created = (await create_suite(client, world.key, "Smoke", description="Old")).json()
    await create_suite_id(client, world.key, "Nightly")
    recording_live_event_publisher.events.clear()

    renamed = await client.patch(f"/api/projects/{world.key}/suites/{created['id']}", json={"name": "Release"})
    cleared = await client.patch(f"/api/projects/{world.key}/suites/{created['id']}", json={"description": None})
    taken = await client.patch(f"/api/projects/{world.key}/suites/{created['id']}", json={"name": "nightly"})

    assert renamed.status_code == 200, renamed.text
    assert (renamed.json()["name"], renamed.json()["description"]) == ("Release", "Old")
    assert (cleared.json()["name"], cleared.json()["description"]) == ("Release", None)
    assert (taken.status_code, taken.json()["code"]) == (409, "SUITE_NAME_ALREADY_USED")
    changed = [event for event in recording_live_event_publisher.events if event.type is LiveEventType.SUITE_CHANGED]
    assert len(changed) == 2


async def test_an_archived_suite_is_hidden_and_read_only(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world)

    archived = await archive_suite(client, world.key, suite_id)
    archived_again = await archive_suite(client, world.key, suite_id)

    assert archived.status_code == 200
    assert archived.json()["archivedAt"] is not None
    assert archived_again.json()["archivedAt"] == archived.json()["archivedAt"]
    assert (await client.get(f"/api/projects/{world.key}/suites")).json() == []
    with_archived = (await client.get(f"/api/projects/{world.key}/suites", params={"archived": "true"})).json()
    assert [suite["id"] for suite in with_archived] == [suite_id]
    for response in (
        await set_suite_cases(client, world.key, suite_id, []),
        await add_cases_by_filter(client, world.key, suite_id, storyKey=world.first_story.jira_key),
        await client.patch(f"/api/projects/{world.key}/suites/{suite_id}", json={"name": "Other"}),
    ):
        assert (response.status_code, response.json()["code"]) == (409, "SUITE_ARCHIVED")


async def test_add_by_filter_adds_each_match_once_after_the_current_cases(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world, case_ids=[world.case_ids[3]])

    added = await add_cases_by_filter(client, world.key, suite_id, storyKey=world.second_story.jira_key.lower())
    added_again = await add_cases_by_filter(client, world.key, suite_id, storyKey=world.second_story.jira_key)

    assert added.status_code == 200, added.text
    assert added.json()["addedCount"] == 1
    assert [case["testCaseId"] for case in added.json()["suite"]["cases"]] == [
        str(world.case_ids[3]),
        str(world.case_ids[2]),
    ]
    assert added_again.json()["addedCount"] == 0


async def test_add_by_filter_needs_every_label_and_one_of_the_priorities(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    smoke_id = await create_label_id(client, world.key, "Smoke")
    payments_id = await create_label_id(client, world.key, "Payments")
    codes = [await find_case_code(container, case_id) for case_id in world.case_ids]
    for code, label_ids in zip(codes, [[smoke_id, payments_id], [smoke_id], [smoke_id, payments_id], []], strict=True):
        assert (await set_case_labels(client, world.key, code, label_ids)).status_code == 200
    await set_priority(container, world.case_ids[0], "critical")
    await set_priority(container, world.case_ids[2], "low")
    suite_id = await create_suite_id(client, world.key)

    by_labels = await add_cases_by_filter(client, world.key, suite_id, labels=["smoke", "PAYMENTS"])
    other_suite_id = await create_suite_id(client, world.key, "Critical")
    by_labels_and_priority = await add_cases_by_filter(
        client, world.key, other_suite_id, labels=["Smoke"], priorities=["critical", "high"]
    )

    assert [case["code"] for case in by_labels.json()["suite"]["cases"]] == [codes[0], codes[2]]
    assert [case["code"] for case in by_labels_and_priority.json()["suite"]["cases"]] == [codes[0]]


async def test_add_by_filter_takes_a_sprint_and_skips_deprecated_cases(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    sprint_id = await seed_sprint(
        container,
        InsightWorld(
            project=world.project, user_id=world.runner.account.user_id, environment_id=world.first_story.environment_id
        ),
        SprintState.ACTIVE,
        None,
    )
    async with container.database.begin():
        await container.database.get_current_session().execute(
            update(StoryTable).where(StoryTable.id == world.first_story.story_id).values(sprint_id=sprint_id)
        )
    await change_case_status(container, world.case_ids[1], "deprecated")
    suite_id = await create_suite_id(client, world.key)

    response = await add_cases_by_filter(client, world.key, suite_id, sprintId=str(sprint_id))

    assert [case["testCaseId"] for case in response.json()["suite"]["cases"]] == [str(world.case_ids[0])]


async def test_add_by_filter_needs_a_known_filter(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    suite_id = await create_suite_id(client, world.key)
    other_project = await seed_project(container)
    other_world = InsightWorld(
        project=other_project, user_id=world.runner.account.user_id, environment_id=world.first_story.environment_id
    )
    foreign_sprint_id = await seed_sprint(container, other_world, SprintState.ACTIVE, None)

    empty = await add_cases_by_filter(client, world.key, suite_id)
    unknown_story = await add_cases_by_filter(client, world.key, suite_id, storyKey="NOPE-1")
    foreign_sprint = await add_cases_by_filter(client, world.key, suite_id, sprintId=str(foreign_sprint_id))

    assert (empty.status_code, empty.json()["code"]) == (422, "INVALID_REQUEST")
    assert (unknown_story.status_code, unknown_story.json()["code"]) == (422, "UNKNOWN_REFERENCE")
    assert (foreign_sprint.status_code, foreign_sprint.json()["code"]) == (422, "UNKNOWN_REFERENCE")


async def test_deleting_a_label_leaves_the_suite_cases_in_place(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    smoke_id = await create_label_id(client, world.key, "Smoke")
    code = await find_case_code(container, world.case_ids[0])
    assert (await set_case_labels(client, world.key, code, [smoke_id])).status_code == 200
    suite_id = await create_suite_id(client, world.key)
    assert (await add_cases_by_filter(client, world.key, suite_id, labels=["Smoke"])).json()["addedCount"] == 1

    deleted = await delete_label(client, world.key, smoke_id)

    assert deleted.status_code == 204
    assert [case["code"] for case in (await get_suite(client, world.key, suite_id)).json()["cases"]] == [code]


async def test_unknown_or_foreign_suite_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    other_project = await seed_project(container)
    await add_member(container, other_project, world.runner.account.user_id, ProjectRole.QC)
    foreign_suite_id = await create_suite_id(client, other_project.key, DEFAULT_SUITE_NAME)

    response = await get_suite(client, world.key, foreign_suite_id)

    assert (response.status_code, response.json()["code"]) == (404, "NOT_FOUND")


def build_foreign_suite_write(
    route: str, world: SuiteWorld, suite_id: str
) -> tuple[str, str, dict[str, object] | None]:
    suite_url = f"/api/projects/{world.key}/suites/{suite_id}"
    writes: dict[str, tuple[str, str, dict[str, object] | None]] = {
        "update": ("PATCH", suite_url, {"name": "Taken over"}),
        "archive": ("POST", f"{suite_url}/archive", None),
        "set_cases": ("PUT", f"{suite_url}/cases", {"testCaseIds": [str(world.case_ids[0])]}),
        "add_by_filter": ("POST", f"{suite_url}/cases/by-filter", {"storyKey": world.first_story.jira_key}),
        "start_manual_run": ("POST", f"/api/projects/{world.key}/runs", {"suiteId": suite_id}),
    }
    return writes[route]


@pytest.mark.parametrize("route", ["update", "archive", "set_cases", "add_by_filter", "start_manual_run"])
async def test_a_foreign_suite_is_not_found_on_every_write(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer, route: str
) -> None:
    world = await seed_world(client, container, recording_mailer)
    other_project = await seed_project(container)
    await add_member(container, other_project, world.runner.account.user_id, ProjectRole.QC)
    foreign_suite_id = await create_suite_id(client, other_project.key, DEFAULT_SUITE_NAME)
    method, url, body = build_foreign_suite_write(route, world, foreign_suite_id)

    response = await client.request(method, url, json=body)

    assert (response.status_code, response.json()["code"]) == (404, "NOT_FOUND")
    foreign_suite = (await get_suite(client, other_project.key, foreign_suite_id)).json()
    assert (foreign_suite["name"], foreign_suite["archivedAt"], foreign_suite["cases"]) == (
        DEFAULT_SUITE_NAME,
        None,
        [],
    )

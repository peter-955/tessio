from uuid import UUID

import pytest
from httpx import AsyncClient
from pydantic import JsonValue

from app.container import Container
from app.modules.shared_steps import CreateSharedStepUseCase, SharedStep, SharedStepAction
from app.modules.shared_steps.errors import SharedStepKeyAlreadyUsedError
from app.modules.shared_steps.infrastructure import PostgresSharedStepRepository
from app.modules.users import WorkspaceRole
from app.shared.events import LiveEventType
from app.shared.permissions import Actor
from tests.api.shared_steps.shared_step_steps import (
    create_case_with,
    create_shared_step,
    create_shared_step_json,
    set_up_shared_step_project,
    shared_step_path,
    update_shared_step,
)
from tests.api.test_cases.case_steps import change_status, create_case
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def test_a_shared_step_is_created_as_version_1_with_its_data_keys(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)

    response = await create_shared_step(client, world.key, key="  Log_In ")

    assert response.status_code == 201, response.text
    content = response.json()
    assert content["key"] == "log_in"
    assert content["title"] == "Log in"
    assert content["isArchived"] is False
    assert content["usageCount"] == 0
    assert content["currentVersion"]["number"] == 1
    assert content["currentVersion"]["dataKeys"] == ["base_url"]
    assert content["currentVersion"]["steps"] == [
        {"order": 1, "action": "Open {{data.base_url}}/sign-in", "expected": "The sign-in form is shown"},
        {"order": 2, "action": "Sign in as {{param.role}}", "expected": "The dashboard is shown"},
    ]
    event = recording_live_event_publisher.events[-1]
    assert event.type is LiveEventType.SHARED_STEP_CHANGED
    assert event.ids["sharedStepKey"] == "log_in"


async def test_a_key_is_used_once_per_project(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await create_shared_step_json(client, world.key)

    response = await create_shared_step(client, world.key, key="LOG_IN")

    assert response.status_code == 409
    assert response.json()["code"] == "SHARED_STEP_KEY_ALREADY_USED"


def build_action(action: str) -> SharedStepAction:
    return SharedStepAction(order=1, action=action, expected=None)


class KeyCheckRacingRepository(PostgresSharedStepRepository):
    async def find_by_key(self, project_id: UUID, key: str) -> SharedStep | None:
        return None


async def test_a_create_that_loses_the_race_for_a_key_gets_the_coded_error(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await create_shared_step_json(client, world.key)
    racing_create = CreateSharedStepUseCase(
        container.database,
        container.project_access_resolver,
        KeyCheckRacingRepository(container.database),
        container.live_event_publisher,
    )
    actor = Actor(user_id=world.runner.account.user_id, workspace_role=WorkspaceRole.MEMBER)

    with pytest.raises(SharedStepKeyAlreadyUsedError):
        await racing_create.execute(actor, world.key, "log_in", "Log in again", [build_action("Open the app")])

    listed = await client.get(shared_step_path(world.key))
    assert [step["title"] for step in listed.json()] == ["Log in"]


def build_actions(count: int) -> list[JsonValue]:
    return [{"action": f"Do step {index}"} for index in range(1, count + 1)]


async def test_a_case_cannot_expand_to_more_than_200_steps(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    for key in ("first", "second", "third", "fourth"):
        await create_shared_step_json(client, world.key, key=key, steps=build_actions(50))
    four_shared_steps: list[JsonValue] = [{"sharedStepKey": key} for key in ("first", "second", "third", "fourth")]

    at_the_limit = await create_case(client, world.key, world.story.jira_key, steps=four_shared_steps)
    over_the_limit = await create_case(
        client, world.key, world.story.jira_key, steps=[*four_shared_steps, {"action": "One more"}]
    )

    assert at_the_limit.status_code == 201, at_the_limit.text
    assert over_the_limit.status_code == 422
    assert over_the_limit.json() == {
        "code": "INVALID_STEP_SHAPE",
        "message": "With its shared steps expanded, this case has 201 steps. "
        "A case can have at most 200 steps once its shared steps are expanded.",
    }


async def test_a_shared_step_save_that_makes_a_case_too_long_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    for key in ("first", "second", "third"):
        await create_shared_step_json(client, world.key, key=key, steps=build_actions(50))
    await create_shared_step_json(client, world.key, key="fourth", steps=build_actions(49))
    long_steps: list[JsonValue] = [{"sharedStepKey": key} for key in ("first", "second", "third", "fourth")]
    long_code = await create_case_with(client, world.key, world.story.jira_key, steps=[*long_steps, {"action": "Pay"}])
    await create_case_with(client, world.key, world.story.jira_key, steps=[{"sharedStepKey": "fourth"}])

    refused = await update_shared_step(client, world.key, "fourth", 1, steps=build_actions(50))
    accepted = await update_shared_step(client, world.key, "fourth", 1, steps=build_actions(48))

    assert refused.status_code == 422
    assert refused.json() == {
        "code": "INVALID_STEP_SHAPE",
        "message": "With these steps, these cases would have more than 200 steps "
        f"once their shared steps are expanded: {long_code}.",
    }
    assert accepted.status_code == 200, accepted.text
    assert accepted.json()["currentVersion"]["number"] == 2


async def test_a_bad_key_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)

    response = await create_shared_step(client, world.key, key="log in")

    assert response.status_code == 422
    assert response.json()["code"] == "INVALID_REQUEST"


async def test_a_shared_step_cannot_contain_a_shared_step_or_an_empty_action(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)

    nested = await create_shared_step(client, world.key, key="nested", steps=[{"sharedStepKey": "log_in"}])
    empty = await create_shared_step(client, world.key, key="empty", steps=[{"action": "  ", "expected": "x"}])

    assert nested.status_code == 422
    assert nested.json() == {
        "code": "INVALID_STEP_SHAPE",
        "message": "Step 1: a shared step cannot contain another shared step.",
    }
    assert empty.status_code == 422
    assert empty.json()["code"] == "INVALID_STEP_SHAPE"


async def test_saving_new_steps_adds_a_version_and_a_title_change_does_not(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await create_shared_step_json(client, world.key)

    renamed = await update_shared_step(client, world.key, "log_in", 1, title="Sign in")
    saved = await update_shared_step(
        client, world.key, "log_in", 1, steps=[{"action": "Sign in with SSO", "expected": "Signed in"}]
    )
    same = await update_shared_step(
        client, world.key, "LOG_IN", 2, steps=[{"action": "Sign in with SSO", "expected": "Signed in"}]
    )

    assert renamed.status_code == 200, renamed.text
    assert renamed.json()["title"] == "Sign in"
    assert renamed.json()["currentVersion"]["number"] == 1
    assert saved.status_code == 200, saved.text
    assert saved.json()["currentVersion"]["number"] == 2
    assert saved.json()["currentVersion"]["steps"] == [
        {"order": 1, "action": "Sign in with SSO", "expected": "Signed in"}
    ]
    assert saved.json()["currentVersion"]["dataKeys"] == []
    assert same.status_code == 200, same.text
    assert same.json()["currentVersion"]["number"] == 2


async def test_a_save_on_an_old_version_is_refused(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await create_shared_step_json(client, world.key)
    await update_shared_step(client, world.key, "log_in", 1, steps=[{"action": "Sign in"}])

    response = await update_shared_step(client, world.key, "log_in", 1, steps=[{"action": "Sign in again"}])

    assert response.status_code == 409
    assert response.json()["code"] == "CONFLICT"


async def test_archived_shared_steps_are_listed_only_when_asked(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await create_shared_step_json(client, world.key, key="log_in")
    await create_shared_step_json(client, world.key, key="add_to_cart", title="Add to cart")

    archived = await update_shared_step(client, world.key, "log_in", 1, archived=True)
    active = await client.get(shared_step_path(world.key))
    everything = await client.get(shared_step_path(world.key), params={"archived": "true"})
    restored = await update_shared_step(client, world.key, "log_in", 1, archived=False)

    assert archived.status_code == 200, archived.text
    assert archived.json()["isArchived"] is True
    assert archived.json()["archivedAt"] is not None
    assert [step["key"] for step in active.json()] == ["add_to_cart"]
    assert [step["key"] for step in everything.json()] == ["add_to_cart", "log_in"]
    assert restored.json()["isArchived"] is False


async def test_usage_counts_the_cases_whose_current_version_uses_the_step(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await set_up_shared_step_project(client, container, recording_mailer)
    await create_shared_step_json(client, world.key)
    story_key = world.story.jira_key
    first = await create_case_with(
        client,
        world.key,
        story_key,
        steps=[{"sharedStepKey": "log_in"}, {"action": "Pay"}, {"sharedStepKey": "log_in"}],
    )
    second = await create_case_with(client, world.key, story_key, steps=[{"sharedStepKey": "log_in"}])
    await create_case_with(client, world.key, story_key, steps=[{"action": "Browse"}])
    deprecated = await create_case_with(client, world.key, story_key, steps=[{"sharedStepKey": "log_in"}])
    await change_status(client, world.key, deprecated, "deprecated")

    detail = await client.get(shared_step_path(world.key, "log_in"))
    listed = await client.get(shared_step_path(world.key))
    usage = await client.get(f"{shared_step_path(world.key, 'log_in')}/usage")

    assert detail.json()["usageCount"] == 2
    assert listed.json()[0]["usageCount"] == 2
    assert usage.status_code == 200, usage.text
    assert [(case["code"], case["status"], case["storyJiraKey"]) for case in usage.json()] == [
        (first, "draft", story_key),
        (second, "draft", story_key),
    ]


async def test_another_projects_shared_step_is_not_found(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    other = await set_up_shared_step_project(client, container, recording_mailer)
    await create_shared_step_json(client, other.key, key="secret_flow")
    world = await set_up_shared_step_project(client, container, recording_mailer)

    detail = await client.get(shared_step_path(world.key, "secret_flow"))
    usage = await client.get(f"{shared_step_path(world.key, 'secret_flow')}/usage")
    update = await update_shared_step(client, world.key, "secret_flow", 1, title="Mine")

    assert [detail.status_code, usage.status_code, update.status_code] == [404, 404, 404]

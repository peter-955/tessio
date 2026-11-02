from httpx import AsyncClient

from app.container import Container
from app.shared.events import LiveEventType
from tests.api.plans.plan_steps import (
    read_plan,
    run_story,
    seed_plan,
    set_failures_status,
    sign_off_plan,
    story_item,
    suite_item,
)
from tests.api.projects.user_steps import use_session
from tests.api.suites.suite_steps import SuiteWorld, raise_story_gap, seed_suite, seed_suite_world
from tests.conftest import RecordingMailer
from tests.support.recording_live_event_publisher import RecordingLiveEventPublisher


async def seed_world(client: AsyncClient, container: Container, recording_mailer: RecordingMailer) -> SuiteWorld:
    return await seed_suite_world(client, container, recording_mailer)


async def test_sign_off_is_refused_while_a_failure_on_the_plans_cases_is_active(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_world(client, container, recording_mailer)
    plan_id = await seed_plan(client, world, [story_item(world.first_story)])
    await run_story(client, world, world.first_story, ["failed", "failed"])
    use_session(client, world.runner.account.session_token)
    recording_live_event_publisher.events.clear()

    refused = await sign_off_plan(client, world.key, plan_id)

    assert refused.status_code == 409
    assert refused.json()["code"] == "PLAN_FAILURES_ACTIVE"
    assert "2 active failures" in refused.json()["message"]
    assert (await read_plan(client, world.key, plan_id))["status"] == "open"
    assert recording_live_event_publisher.events == []


async def test_fixed_and_reopened_failures_still_block_and_verified_ones_do_not(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    plan_id = await seed_plan(client, world, [story_item(world.first_story)])
    await run_story(client, world, world.first_story, ["failed", "passed"])
    use_session(client, world.runner.account.session_token)
    failing_case_id = world.first_story.case_ids[0]

    await set_failures_status(container, failing_case_id, "fixed")
    while_fixed = await sign_off_plan(client, world.key, plan_id)
    await set_failures_status(container, failing_case_id, "reopened")
    while_reopened = await sign_off_plan(client, world.key, plan_id)
    await set_failures_status(container, failing_case_id, "verified")
    after_verify = await sign_off_plan(client, world.key, plan_id)

    assert [while_fixed.json()["code"], while_reopened.json()["code"]] == ["PLAN_FAILURES_ACTIVE"] * 2
    assert "1 active failure " in while_fixed.json()["message"]
    assert after_verify.status_code == 200, after_verify.text


async def test_a_failure_outside_the_plan_does_not_block_its_sign_off(
    client: AsyncClient, container: Container, recording_mailer: RecordingMailer
) -> None:
    world = await seed_world(client, container, recording_mailer)
    suite_id = await seed_suite(client, world, case_ids=[world.first_story.case_ids[0]])
    plan_id = await seed_plan(client, world, [suite_item(suite_id)])
    await run_story(client, world, world.first_story, ["passed", "failed"])
    await run_story(client, world, world.second_story, ["failed", "failed"])
    use_session(client, world.runner.account.session_token)

    response = await sign_off_plan(client, world.key, plan_id)

    assert response.status_code == 200, response.text


async def test_sign_off_records_who_and_when_and_publishes_both_events(
    client: AsyncClient,
    container: Container,
    recording_mailer: RecordingMailer,
    recording_live_event_publisher: RecordingLiveEventPublisher,
) -> None:
    world = await seed_world(client, container, recording_mailer)
    plan_id = await seed_plan(client, world, [story_item(world.first_story)])
    await run_story(client, world, world.first_story, ["passed", "passed"])
    await raise_story_gap(client, world, world.first_story)
    recording_live_event_publisher.events.clear()

    response = await sign_off_plan(client, world.key, plan_id)

    assert response.status_code == 200, response.text
    body = response.json()
    assert body["status"] == "signed_off"
    assert body["signedOffBy"] == str(world.runner.account.user_id)
    assert body["signedOffByName"] == "Quinn Runner"
    assert body["signedOffAt"] is not None
    assert body["closedAt"] is None
    assert [(event.type, event.ids, event.project_id) for event in recording_live_event_publisher.events] == [
        (LiveEventType.PLAN_CHANGED, {"planId": plan_id}, world.project.id),
        (LiveEventType.PLAN_SIGNED_OFF, {"planId": plan_id}, world.project.id),
    ]

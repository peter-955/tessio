import asyncio
import uuid
from collections.abc import AsyncIterator
from datetime import timedelta

from app.modules.live_events import StreamLiveEventsUseCase
from app.shared.events import LiveEvent, LiveEventType
from app.shared.permissions import Actor, WorkspaceRole
from tests.api.live_events.live_events_test_container import LiveEventsTestContainer
from tests.api.live_events.static_project_access_resolver import StaticProjectAccessResolver

RECEIVE_TIMEOUT_SECONDS = 5


def build_actor() -> Actor:
    return Actor(user_id=uuid.uuid4(), workspace_role=WorkspaceRole.MEMBER)


def build_sentinel(actor: Actor) -> LiveEvent:
    return LiveEvent(type=LiveEventType.NOTIFICATION_CREATED, user_id=actor.user_id, ids={"sentinel": "true"})


def build_project_event(project_id: uuid.UUID) -> LiveEvent:
    return LiveEvent(type=LiveEventType.GAP_CHANGED, project_id=project_id, ids={"gapId": str(uuid.uuid4())})


async def receive(stream: AsyncIterator[LiveEvent]) -> LiveEvent:
    return await asyncio.wait_for(anext(stream), RECEIVE_TIMEOUT_SECONDS)


async def test_user_event_reaches_only_that_user(container: LiveEventsTestContainer) -> None:
    recipient = build_actor()
    bystander = build_actor()
    event = LiveEvent(type=LiveEventType.NOTIFICATION_CREATED, user_id=recipient.user_id, ids={"notificationId": "1"})

    async with (
        container.stream_live_events.open_stream(recipient) as recipient_stream,
        container.stream_live_events.open_stream(bystander) as bystander_stream,
    ):
        await container.live_event_publisher.publish(event)
        await container.live_event_publisher.publish(build_sentinel(bystander))

        assert await receive(recipient_stream) == event
        assert await receive(bystander_stream) == build_sentinel(bystander)


async def test_project_event_reaches_members_only(
    container: LiveEventsTestContainer, project_access_resolver: StaticProjectAccessResolver
) -> None:
    member = build_actor()
    non_member = build_actor()
    project_id = uuid.uuid4()
    project_access_resolver.project_ids_by_user_id[member.user_id] = {project_id}
    event = build_project_event(project_id)

    async with (
        container.stream_live_events.open_stream(member) as member_stream,
        container.stream_live_events.open_stream(non_member) as non_member_stream,
    ):
        await container.live_event_publisher.publish(event)
        await container.live_event_publisher.publish(build_sentinel(non_member))

        assert await receive(member_stream) == event
        assert await receive(non_member_stream) == build_sentinel(non_member)


async def test_members_changed_refreshes_project_access(
    container: LiveEventsTestContainer, project_access_resolver: StaticProjectAccessResolver
) -> None:
    newcomer = build_actor()
    project_id = uuid.uuid4()
    use_case = StreamLiveEventsUseCase(
        container.database, container.live_event_hub, project_access_resolver, timedelta(hours=1)
    )
    members_changed = LiveEvent(type=LiveEventType.PROJECT_MEMBERS_CHANGED, project_id=project_id)
    event = build_project_event(project_id)

    async with use_case.open_stream(newcomer) as newcomer_stream:
        project_access_resolver.project_ids_by_user_id[newcomer.user_id] = {project_id}
        await container.live_event_publisher.publish(build_project_event(project_id))
        await container.live_event_publisher.publish(build_sentinel(newcomer))
        await container.live_event_publisher.publish(members_changed)
        await container.live_event_publisher.publish(event)

        assert await receive(newcomer_stream) == build_sentinel(newcomer)
        assert await receive(newcomer_stream) == members_changed
        assert await receive(newcomer_stream) == event


async def test_project_access_is_refreshed_after_the_interval(
    container: LiveEventsTestContainer, project_access_resolver: StaticProjectAccessResolver
) -> None:
    newcomer = build_actor()
    project_id = uuid.uuid4()
    event = build_project_event(project_id)

    async with container.stream_live_events.open_stream(newcomer) as newcomer_stream:
        project_access_resolver.project_ids_by_user_id[newcomer.user_id] = {project_id}
        await container.live_event_publisher.publish(event)

        assert await receive(newcomer_stream) == event


async def test_removed_member_stops_receiving_project_events(
    container: LiveEventsTestContainer, project_access_resolver: StaticProjectAccessResolver
) -> None:
    former_member = build_actor()
    project_id = uuid.uuid4()
    project_access_resolver.project_ids_by_user_id[former_member.user_id] = {project_id}

    async with container.stream_live_events.open_stream(former_member) as former_member_stream:
        project_access_resolver.project_ids_by_user_id[former_member.user_id] = set()
        await container.live_event_publisher.publish(
            LiveEvent(type=LiveEventType.PROJECT_MEMBERS_CHANGED, project_id=project_id)
        )
        await container.live_event_publisher.publish(build_project_event(project_id))
        await container.live_event_publisher.publish(build_sentinel(former_member))

        assert await receive(former_member_stream) == build_sentinel(former_member)


async def test_event_without_user_or_project_is_dropped(container: LiveEventsTestContainer) -> None:
    listener = build_actor()

    async with container.stream_live_events.open_stream(listener) as listener_stream:
        await container.live_event_publisher.publish(LiveEvent(type=LiveEventType.STORY_CHANGED))
        await container.live_event_publisher.publish(build_sentinel(listener))

        assert await receive(listener_stream) == build_sentinel(listener)

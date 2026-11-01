import asyncio
import json
import uuid
from collections.abc import AsyncIterator

import pytest
from redis.asyncio import Redis

from app.shared.events import (
    LIVE_EVENTS_CHANNEL,
    SUBSCRIPTION_BUFFER_SIZE,
    LiveEvent,
    LiveEventSubscription,
    LiveEventType,
    RedisLiveEventHub,
    RedisLiveEventPublisher,
)

RECEIVE_TIMEOUT_SECONDS = 5
SILENCE_TIMEOUT_SECONDS = 0.3


@pytest.fixture
async def hub(redis_url: str) -> AsyncIterator[RedisLiveEventHub]:
    live_event_hub = RedisLiveEventHub(redis_url)
    yield live_event_hub
    await live_event_hub.close()


@pytest.fixture
async def publisher(redis_url: str) -> AsyncIterator[RedisLiveEventPublisher]:
    live_event_publisher = RedisLiveEventPublisher(redis_url)
    yield live_event_publisher
    await live_event_publisher.close()


def build_event() -> LiveEvent:
    return LiveEvent(type=LiveEventType.RUN_CASE_RECORDED, user_id=uuid.uuid4(), ids={"runId": str(uuid.uuid4())})


async def receive(subscription: LiveEventSubscription) -> LiveEvent:
    return await asyncio.wait_for(anext(subscription), RECEIVE_TIMEOUT_SECONDS)


async def receive_buffered(subscription: LiveEventSubscription) -> list[LiveEvent]:
    events: list[LiveEvent] = []
    while True:
        try:
            events.append(await asyncio.wait_for(anext(subscription), SILENCE_TIMEOUT_SECONDS))
        except TimeoutError, StopAsyncIteration:
            return events


async def test_published_event_reaches_the_subscriber(
    hub: RedisLiveEventHub, publisher: RedisLiveEventPublisher
) -> None:
    event = build_event()

    async with hub.subscribe() as subscription:
        await publisher.publish(event)

        assert await receive(subscription) == event


async def test_event_is_published_as_camel_case_json(redis_url: str, publisher: RedisLiveEventPublisher) -> None:
    project_id = uuid.uuid4()
    event = LiveEvent(type=LiveEventType.STORY_CHANGED, project_id=project_id, ids={"storyId": "story-1"})
    redis = Redis.from_url(redis_url, decode_responses=True)
    pubsub = redis.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(LIVE_EVENTS_CHANNEL)
    try:
        await publisher.publish(event)
        message = await asyncio.wait_for(anext(pubsub.listen()), RECEIVE_TIMEOUT_SECONDS)
    finally:
        await redis.aclose()

    assert message["channel"] == LIVE_EVENTS_CHANNEL
    assert json.loads(message["data"]) == {
        "type": "story.changed",
        "projectId": str(project_id),
        "userId": None,
        "ids": {"storyId": "story-1"},
    }


async def test_every_subscriber_receives_the_event(hub: RedisLiveEventHub, publisher: RedisLiveEventPublisher) -> None:
    event = build_event()

    async with hub.subscribe() as first_subscription, hub.subscribe() as second_subscription:
        await publisher.publish(event)

        assert await receive(first_subscription) == event
        assert await receive(second_subscription) == event


async def test_invalid_message_is_skipped(
    redis_url: str, hub: RedisLiveEventHub, publisher: RedisLiveEventPublisher
) -> None:
    event = build_event()
    redis = Redis.from_url(redis_url, decode_responses=True)

    async with hub.subscribe() as subscription:
        try:
            await redis.publish(LIVE_EVENTS_CHANNEL, "not json")
            await redis.publish(LIVE_EVENTS_CHANNEL, '{"type": "unknown.event"}')
        finally:
            await redis.aclose()
        await publisher.publish(event)

        assert await receive(subscription) == event


async def test_full_buffer_drops_events_without_blocking_other_subscribers(
    hub: RedisLiveEventHub, publisher: RedisLiveEventPublisher
) -> None:
    events = [build_event() for _ in range(SUBSCRIPTION_BUFFER_SIZE + 5)]

    async with hub.subscribe() as idle_subscription, hub.subscribe() as reading_subscription:
        received_events: list[LiveEvent] = []
        for event in events:
            await publisher.publish(event)
            received_events.append(await receive(reading_subscription))

        assert received_events == events
        assert await receive_buffered(idle_subscription) == events[:SUBSCRIPTION_BUFFER_SIZE]


async def test_closed_subscription_receives_nothing(hub: RedisLiveEventHub, publisher: RedisLiveEventPublisher) -> None:
    async with hub.subscribe() as subscription:
        pass

    await publisher.publish(build_event())

    assert [event async for event in subscription] == []


async def test_closing_the_hub_ends_open_subscriptions(
    hub: RedisLiveEventHub, publisher: RedisLiveEventPublisher
) -> None:
    async with hub.subscribe() as subscription:
        await hub.close()
        await publisher.publish(build_event())

        assert await asyncio.wait_for(receive_buffered(subscription), RECEIVE_TIMEOUT_SECONDS) == []


async def test_hub_restarts_after_close(hub: RedisLiveEventHub, publisher: RedisLiveEventPublisher) -> None:
    event = build_event()
    async with hub.subscribe():
        pass
    await hub.close()

    async with hub.subscribe() as subscription:
        await publisher.publish(event)

        assert await receive(subscription) == event


async def test_hub_resubscribes_after_its_connection_is_killed(
    redis_url: str, hub: RedisLiveEventHub, publisher: RedisLiveEventPublisher
) -> None:
    redis = Redis.from_url(redis_url, decode_responses=True)

    async with hub.subscribe() as subscription:
        try:
            await redis.client_kill_filter(_type="pubsub")
        finally:
            await redis.aclose()
        received_event = await asyncio.wait_for(publish_until_received(publisher, subscription), 10)

    assert received_event.type is LiveEventType.RUN_CASE_RECORDED


async def publish_until_received(publisher: RedisLiveEventPublisher, subscription: LiveEventSubscription) -> LiveEvent:
    while True:
        await publisher.publish(build_event())
        try:
            return await asyncio.wait_for(anext(subscription), SILENCE_TIMEOUT_SECONDS)
        except TimeoutError:
            continue

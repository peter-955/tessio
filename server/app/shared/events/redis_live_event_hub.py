import asyncio
from collections.abc import AsyncIterator, Mapping
from contextlib import asynccontextmanager, suppress

from pydantic import ValidationError
from redis.asyncio import Redis
from redis.asyncio.client import PubSub
from redis.exceptions import RedisError

from app.shared.events.live_event import LiveEvent
from app.shared.events.live_event_constant import LIVE_EVENTS_CHANNEL, RECONNECT_DELAY
from app.shared.events.live_event_hub import LiveEventHub
from app.shared.events.live_event_subscription import LiveEventSubscription
from app.shared.logging import get_logger

log = get_logger(__name__)


class RedisLiveEventHub(LiveEventHub):
    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._redis: Redis | None = None
        self._pubsub: PubSub | None = None
        self._listener: asyncio.Task[None] | None = None
        self._subscriptions: set[LiveEventSubscription] = set()
        self._start_lock = asyncio.Lock()

    @asynccontextmanager
    async def subscribe(self) -> AsyncIterator[LiveEventSubscription]:
        await self._start()
        subscription = LiveEventSubscription()
        self._subscriptions.add(subscription)
        try:
            yield subscription
        finally:
            self._subscriptions.discard(subscription)
            subscription.close()

    async def close(self) -> None:
        listener = self._listener
        self._listener = None
        if listener is not None:
            listener.cancel()
            with suppress(asyncio.CancelledError):
                await listener
        pubsub = self._pubsub
        self._pubsub = None
        if pubsub is not None:
            with suppress(RedisError):
                await pubsub.unsubscribe(LIVE_EVENTS_CHANNEL)
        redis = self._redis
        self._redis = None
        if redis is not None:
            await redis.aclose()
        for subscription in tuple(self._subscriptions):
            subscription.close()
        self._subscriptions.clear()

    async def _start(self) -> None:
        async with self._start_lock:
            if self._listener is not None and not self._listener.done():
                return
            pubsub = self._get_pubsub()
            await pubsub.subscribe(LIVE_EVENTS_CHANNEL)
            self._listener = asyncio.create_task(self._listen(pubsub))

    async def _listen(self, pubsub: PubSub) -> None:
        while True:
            try:
                async for message in pubsub.listen():
                    self._dispatch(message)
                return
            except RedisError as error:
                log.warning("live_event.hub_disconnected", extra={"reason": type(error).__name__})
                await asyncio.sleep(RECONNECT_DELAY.total_seconds())

    def _dispatch(self, message: Mapping[str, object]) -> None:
        payload = message.get("data")
        if message.get("type") != "message" or not isinstance(payload, str):
            return
        try:
            event = LiveEvent.model_validate_json(payload)
        except ValidationError:
            log.warning("live_event.invalid_message", extra={"payload_length": len(payload)})
            return
        for subscription in tuple(self._subscriptions):
            subscription.deliver(event)

    def _get_pubsub(self) -> PubSub:
        if self._pubsub is None:
            self._pubsub = self._get_redis().pubsub(ignore_subscribe_messages=True)
        return self._pubsub

    def _get_redis(self) -> Redis:
        if self._redis is None:
            self._redis = Redis.from_url(self._redis_url, decode_responses=True)
        return self._redis

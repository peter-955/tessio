from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.shared.events.live_event import LiveEvent
from app.shared.events.live_event_constant import LIVE_EVENTS_CHANNEL
from app.shared.events.live_event_publisher import LiveEventPublisher
from app.shared.logging import get_logger

log = get_logger(__name__)


class RedisLiveEventPublisher(LiveEventPublisher):
    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._redis: Redis | None = None

    async def publish(self, event: LiveEvent) -> None:
        try:
            await self._get_redis().publish(LIVE_EVENTS_CHANNEL, event.model_dump_json(by_alias=True))
        except RedisError as error:
            log.warning(
                "live_event.publish_failed",
                extra={"event_type": event.type.value, "reason": type(error).__name__},
            )

    async def close(self) -> None:
        if self._redis is not None:
            redis = self._redis
            self._redis = None
            await redis.aclose()

    def _get_redis(self) -> Redis:
        if self._redis is None:
            self._redis = Redis.from_url(self._redis_url, decode_responses=True)
        return self._redis

from redis.asyncio import Redis
from redis.exceptions import RedisError

from app.shared.logging import get_logger
from app.shared.rate_limit.rate_limit_constant import MINIMUM_RETRY_AFTER_SECONDS, RATE_LIMIT_KEY_PREFIX
from app.shared.rate_limit.rate_limit_decision import RateLimitDecision
from app.shared.rate_limit.rate_limit_rule import RateLimitRule
from app.shared.rate_limit.rate_limiter import RateLimiter

log = get_logger(__name__)


class RedisRateLimiter(RateLimiter):
    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url
        self._redis: Redis | None = None

    async def hit(self, key: str, rule: RateLimitRule) -> RateLimitDecision:
        counter_key = f"{RATE_LIMIT_KEY_PREFIX}:{rule.name}:{key}"
        window_seconds = max(int(rule.window.total_seconds()), MINIMUM_RETRY_AFTER_SECONDS)
        try:
            async with self._get_redis().pipeline(transaction=True) as pipeline:
                pipeline.incr(counter_key)
                pipeline.expire(counter_key, window_seconds, nx=True)
                pipeline.ttl(counter_key)
                count, _, time_to_live = await pipeline.execute()
        except RedisError as error:
            log.warning("rate_limit.check_failed", extra={"rule": rule.name, "reason": type(error).__name__})
            return RateLimitDecision(is_allowed=True, retry_after_seconds=0)
        return RateLimitDecision(
            is_allowed=int(count) <= rule.limit,
            retry_after_seconds=max(int(time_to_live), MINIMUM_RETRY_AFTER_SECONDS),
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

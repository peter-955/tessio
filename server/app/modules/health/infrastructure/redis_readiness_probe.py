import inspect

from redis.asyncio import Redis

from app.modules.health.ports.dependency_probe import DependencyProbe


class RedisReadinessProbe(DependencyProbe):
    def __init__(self, redis_url: str) -> None:
        self._redis_url = redis_url

    async def is_reachable(self) -> bool:
        client = Redis.from_url(self._redis_url)
        try:
            reply = client.ping()
            is_reachable = await reply if inspect.isawaitable(reply) else reply
            return bool(is_reachable)
        finally:
            await client.aclose()

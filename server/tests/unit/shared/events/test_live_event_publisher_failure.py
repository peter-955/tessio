import uuid

from app.shared.events import LiveEvent, LiveEventType, RedisLiveEventPublisher

UNREACHABLE_REDIS_URL = "redis://localhost:1"


async def test_publish_does_not_raise_when_redis_is_unreachable() -> None:
    publisher = RedisLiveEventPublisher(UNREACHABLE_REDIS_URL)
    try:
        await publisher.publish(LiveEvent(type=LiveEventType.NOTIFICATION_CREATED, user_id=uuid.uuid4()))
    finally:
        await publisher.close()

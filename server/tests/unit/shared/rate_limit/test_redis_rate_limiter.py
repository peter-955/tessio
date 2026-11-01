import asyncio
import logging
import uuid
from collections.abc import AsyncIterator
from datetime import timedelta

import pytest
from redis.asyncio import Redis

from app.shared.rate_limit import RateLimitDecision, RateLimitRule, RedisRateLimiter

UNREACHABLE_REDIS_URL = "redis://localhost:1"
WINDOW = timedelta(seconds=2)


@pytest.fixture
async def rate_limiter(redis_url: str) -> AsyncIterator[RedisRateLimiter]:
    redis_rate_limiter = RedisRateLimiter(redis_url)
    yield redis_rate_limiter
    await redis_rate_limiter.close()


def build_rule(limit: int) -> RateLimitRule:
    return RateLimitRule(name=f"test_{uuid.uuid4().hex[:8]}", limit=limit, window=WINDOW)


async def test_requests_are_allowed_up_to_the_limit(rate_limiter: RedisRateLimiter) -> None:
    rule = build_rule(limit=3)

    decisions = [await rate_limiter.hit("10.0.0.1", rule) for _ in range(4)]

    assert [decision.is_allowed for decision in decisions] == [True, True, True, False]
    assert 1 <= decisions[-1].retry_after_seconds <= 2


async def test_keys_and_rules_are_counted_separately(rate_limiter: RedisRateLimiter) -> None:
    first_rule = build_rule(limit=1)
    second_rule = build_rule(limit=1)

    first_key = await rate_limiter.hit("10.0.0.1", first_rule)
    second_key = await rate_limiter.hit("10.0.0.2", first_rule)
    second_rule_decision = await rate_limiter.hit("10.0.0.1", second_rule)
    refused = await rate_limiter.hit("10.0.0.1", first_rule)

    assert first_key.is_allowed
    assert second_key.is_allowed
    assert second_rule_decision.is_allowed
    assert not refused.is_allowed


async def test_the_window_expires_and_counting_starts_again(rate_limiter: RedisRateLimiter) -> None:
    rule = build_rule(limit=1)
    await rate_limiter.hit("10.0.0.1", rule)
    refused = await rate_limiter.hit("10.0.0.1", rule)

    await asyncio.sleep(WINDOW.total_seconds() + 0.2)
    allowed_again = await rate_limiter.hit("10.0.0.1", rule)

    assert not refused.is_allowed
    assert allowed_again.is_allowed


async def test_the_counter_key_expires_with_the_window(rate_limiter: RedisRateLimiter, redis_url: str) -> None:
    rule = build_rule(limit=5)
    await rate_limiter.hit("10.0.0.1", rule)
    await rate_limiter.hit("10.0.0.1", rule)

    redis = Redis.from_url(redis_url, decode_responses=True)
    try:
        counter_key = f"tessio:rate:{rule.name}:10.0.0.1"
        count = await redis.get(counter_key)
        time_to_live = await redis.ttl(counter_key)
    finally:
        await redis.aclose()

    assert count == "2"
    assert 1 <= time_to_live <= 2


async def test_an_unreachable_redis_allows_the_request(caplog: pytest.LogCaptureFixture) -> None:
    rate_limiter = RedisRateLimiter(UNREACHABLE_REDIS_URL)
    try:
        with caplog.at_level(logging.WARNING):
            decision = await rate_limiter.hit("10.0.0.1", build_rule(limit=1))
    finally:
        await rate_limiter.close()

    assert decision == RateLimitDecision(is_allowed=True, retry_after_seconds=0)
    assert [record.getMessage() for record in caplog.records] == ["rate_limit.check_failed"]
    assert caplog.records[0].__dict__["reason"] == "ConnectionError"

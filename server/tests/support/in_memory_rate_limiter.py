from collections import Counter

from app.shared.rate_limit import MINIMUM_RETRY_AFTER_SECONDS, RateLimitDecision, RateLimiter, RateLimitRule


class InMemoryRateLimiter(RateLimiter):
    def __init__(self) -> None:
        self.counts: Counter[tuple[str, str]] = Counter()

    async def hit(self, key: str, rule: RateLimitRule) -> RateLimitDecision:
        self.counts[(rule.name, key)] += 1
        return RateLimitDecision(
            is_allowed=self.counts[(rule.name, key)] <= rule.limit,
            retry_after_seconds=max(int(rule.window.total_seconds()), MINIMUM_RETRY_AFTER_SECONDS),
        )

    async def close(self) -> None:
        return None

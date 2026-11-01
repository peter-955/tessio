from abc import ABC, abstractmethod

from app.shared.rate_limit.rate_limit_decision import RateLimitDecision
from app.shared.rate_limit.rate_limit_rule import RateLimitRule


class RateLimiter(ABC):
    @abstractmethod
    async def hit(self, key: str, rule: RateLimitRule) -> RateLimitDecision: ...

    @abstractmethod
    async def close(self) -> None: ...

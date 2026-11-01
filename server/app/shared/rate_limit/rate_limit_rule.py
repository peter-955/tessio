from datetime import timedelta

from app.shared.common import Entity


class RateLimitRule(Entity):
    name: str
    limit: int
    window: timedelta

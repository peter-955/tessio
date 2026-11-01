from app.shared.common import Entity


class RateLimitDecision(Entity):
    is_allowed: bool
    retry_after_seconds: int

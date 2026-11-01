from datetime import datetime
from uuid import UUID

from app.shared.common import Entity


class UserSession(Entity):
    id: UUID
    user_id: UUID
    token_hash: str
    is_two_factor_passed: bool
    user_agent: str | None
    ip: str | None
    last_seen_at: datetime
    expires_at: datetime
    created_at: datetime

    def is_expired(self, now: datetime) -> bool:
        return now >= self.expires_at

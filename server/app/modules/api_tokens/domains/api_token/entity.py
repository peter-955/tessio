from datetime import datetime
from uuid import UUID

from app.modules.api_tokens.typing.enums import ApiTokenStatus
from app.shared.common import Entity


class ApiToken(Entity):
    id: UUID
    user_id: UUID
    project_id: UUID
    name: str
    prefix: str
    token_hash: str
    expires_at: datetime
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime

    def is_expired(self, now: datetime) -> bool:
        return now >= self.expires_at

    def is_active(self, now: datetime) -> bool:
        return self.revoked_at is None and not self.is_expired(now)

    def resolve_status(self, now: datetime) -> ApiTokenStatus:
        if self.revoked_at is not None:
            return ApiTokenStatus.REVOKED
        if self.is_expired(now):
            return ApiTokenStatus.EXPIRED
        return ApiTokenStatus.ACTIVE

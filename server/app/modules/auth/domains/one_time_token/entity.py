from datetime import datetime
from uuid import UUID

from app.modules.auth.typing.enums import OneTimeTokenPurpose
from app.shared.common import Entity


class OneTimeToken(Entity):
    id: UUID
    user_id: UUID
    purpose: OneTimeTokenPurpose
    token_hash: str
    expires_at: datetime
    used_at: datetime | None
    created_at: datetime

    def is_usable(self, now: datetime) -> bool:
        return self.used_at is None and now < self.expires_at

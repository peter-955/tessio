from datetime import datetime
from uuid import UUID

from app.modules.auth import ApiTokenRevoker


class RecordingApiTokenRevoker(ApiTokenRevoker):
    def __init__(self) -> None:
        self.revoked_user_ids: list[UUID] = []

    async def revoke_all_for_user(self, user_id: UUID, now: datetime) -> None:
        self.revoked_user_ids.append(user_id)

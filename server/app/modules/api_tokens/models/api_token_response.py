from datetime import datetime
from uuid import UUID

from app.modules.api_tokens.typing.enums import ApiTokenStatus
from app.shared.common import WireModel


class ApiTokenResponse(WireModel):
    id: UUID
    name: str
    prefix: str
    project_id: UUID
    project_key: str
    project_name: str
    status: ApiTokenStatus
    expires_at: datetime
    last_used_at: datetime | None
    revoked_at: datetime | None
    created_at: datetime

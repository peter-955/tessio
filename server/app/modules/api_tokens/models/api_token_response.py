from datetime import datetime
from uuid import UUID

from app.modules.api_tokens.typing.enums import ApiTokenScope, ApiTokenStatus
from app.shared.common import WireModel


class ApiTokenResponse(WireModel):
    id: UUID
    name: str
    prefix: str
    project_id: UUID
    project_key: str
    project_name: str
    status: ApiTokenStatus
    scope: ApiTokenScope
    expires_at: datetime
    last_used_at: datetime | None
    plugin_version: str | None
    revoked_at: datetime | None
    created_at: datetime

from datetime import datetime
from uuid import UUID

from app.modules.shared_steps.models.shared_step_version_response import SharedStepVersionResponse
from app.shared.common import WireModel


class SharedStepResponse(WireModel):
    id: UUID
    key: str
    title: str
    is_archived: bool
    archived_at: datetime | None
    current_version: SharedStepVersionResponse
    usage_count: int
    created_by: UUID
    created_at: datetime

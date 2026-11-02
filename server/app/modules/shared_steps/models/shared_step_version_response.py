from datetime import datetime
from uuid import UUID

from app.modules.shared_steps.models.shared_step_action_response import SharedStepActionResponse
from app.shared.common import WireModel


class SharedStepVersionResponse(WireModel):
    id: UUID
    number: int
    steps: list[SharedStepActionResponse]
    data_keys: list[str]
    created_by: UUID
    created_at: datetime

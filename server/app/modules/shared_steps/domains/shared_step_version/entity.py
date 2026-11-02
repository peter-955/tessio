from datetime import datetime
from uuid import UUID

from app.modules.shared_steps.domains.shared_step_action.entity import SharedStepAction
from app.shared.common import Entity


class SharedStepVersion(Entity):
    id: UUID
    shared_step_id: UUID
    number: int
    steps: list[SharedStepAction]
    data_keys: list[str]
    created_by: UUID
    created_at: datetime

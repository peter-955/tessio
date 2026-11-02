from datetime import date
from uuid import UUID

from app.shared.common import Entity


class PlanPatch(Entity):
    name: str | None
    description: str | None
    is_changing_description: bool
    target_date: date | None
    is_changing_target_date: bool
    environment_id: UUID | None
    is_changing_environment: bool

from datetime import date, datetime
from uuid import UUID

from app.modules.plans.typing.enums import PlanStatus
from app.shared.common import Entity


class TestPlan(Entity):
    id: UUID
    project_id: UUID
    name: str
    description: str | None
    target_date: date | None
    environment_id: UUID | None
    status: PlanStatus
    signed_off_by: UUID | None
    signed_off_at: datetime | None
    closed_by: UUID | None
    closed_at: datetime | None
    created_by: UUID
    created_at: datetime

    @property
    def is_open(self) -> bool:
        return self.status is PlanStatus.OPEN

    @property
    def progress_until(self) -> datetime | None:
        return self.signed_off_at or self.closed_at

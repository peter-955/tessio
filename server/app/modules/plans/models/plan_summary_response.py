from datetime import date, datetime
from uuid import UUID

from app.modules.plans.models.plan_progress_counts_response import PlanProgressCountsResponse
from app.modules.plans.typing.enums import PlanStatus
from app.shared.common import WireModel


class PlanSummaryResponse(WireModel):
    id: UUID
    name: str
    description: str | None
    status: PlanStatus
    target_date: date | None
    environment_id: UUID | None
    environment_name: str | None
    item_count: int
    counts: PlanProgressCountsResponse
    created_by: UUID
    created_at: datetime
    signed_off_at: datetime | None
    closed_at: datetime | None

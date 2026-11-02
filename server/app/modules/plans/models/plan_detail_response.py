from datetime import date, datetime
from uuid import UUID

from app.modules.plans.models.plan_item_response import PlanItemResponse
from app.modules.plans.models.plan_progress_response import PlanProgressResponse
from app.modules.plans.typing.enums import PlanStatus
from app.shared.common import WireModel


class PlanDetailResponse(WireModel):
    id: UUID
    name: str
    description: str | None
    status: PlanStatus
    target_date: date | None
    environment_id: UUID | None
    environment_name: str | None
    created_by: UUID
    created_by_name: str | None
    created_at: datetime
    signed_off_by: UUID | None
    signed_off_by_name: str | None
    signed_off_at: datetime | None
    closed_by: UUID | None
    closed_by_name: str | None
    closed_at: datetime | None
    items: list[PlanItemResponse]
    progress: PlanProgressResponse

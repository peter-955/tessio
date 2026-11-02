from pydantic import Field

from app.modules.plans.models.plan_item_request import PlanItemRequest
from app.modules.plans.typing.constants import MAX_PLAN_ITEMS
from app.shared.common import WireModel


class SetPlanItemsRequest(WireModel):
    items: list[PlanItemRequest] = Field(max_length=MAX_PLAN_ITEMS)

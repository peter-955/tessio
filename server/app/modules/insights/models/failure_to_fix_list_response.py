from app.modules.insights.models.failure_to_fix_item_response import FailureToFixItemResponse
from app.shared.common import WireModel


class FailureToFixListResponse(WireModel):
    total_count: int
    items: list[FailureToFixItemResponse]

from app.modules.insights.models.uncovered_criterion_item_response import UncoveredCriterionItemResponse
from app.shared.common import WireModel


class UncoveredCriterionListResponse(WireModel):
    total_count: int
    items: list[UncoveredCriterionItemResponse]

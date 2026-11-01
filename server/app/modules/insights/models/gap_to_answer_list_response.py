from app.modules.insights.models.gap_to_answer_item_response import GapToAnswerItemResponse
from app.shared.common import WireModel


class GapToAnswerListResponse(WireModel):
    total_count: int
    items: list[GapToAnswerItemResponse]

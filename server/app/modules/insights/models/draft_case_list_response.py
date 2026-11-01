from app.modules.insights.models.draft_case_item_response import DraftCaseItemResponse
from app.shared.common import WireModel


class DraftCaseListResponse(WireModel):
    total_count: int
    items: list[DraftCaseItemResponse]

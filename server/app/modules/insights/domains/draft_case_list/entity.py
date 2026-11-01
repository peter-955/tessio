from app.modules.insights.domains.draft_case_item.entity import DraftCaseItem
from app.shared.common import Entity


class DraftCaseList(Entity):
    total_count: int
    items: list[DraftCaseItem]

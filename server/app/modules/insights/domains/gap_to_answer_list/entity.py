from app.modules.insights.domains.gap_to_answer_item.entity import GapToAnswerItem
from app.shared.common import Entity


class GapToAnswerList(Entity):
    total_count: int
    items: list[GapToAnswerItem]

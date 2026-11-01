from app.modules.insights.domains.uncovered_criterion_item.entity import UncoveredCriterionItem
from app.shared.common import Entity


class UncoveredCriterionList(Entity):
    total_count: int
    items: list[UncoveredCriterionItem]

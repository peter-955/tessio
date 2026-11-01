from app.modules.insights.domains.failure_to_fix_item.entity import FailureToFixItem
from app.shared.common import Entity


class FailureToFixList(Entity):
    total_count: int
    items: list[FailureToFixItem]

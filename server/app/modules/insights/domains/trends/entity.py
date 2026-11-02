from app.modules.insights.domains.day_range.entity import DayRange
from app.modules.insights.domains.trend_point.entity import TrendPoint
from app.modules.insights.typing.enums import TrendGrouping
from app.shared.common import Entity


class Trends(Entity):
    grouping: TrendGrouping
    day_range: DayRange
    executors: list[str]
    points: list[TrendPoint]
    total: TrendPoint

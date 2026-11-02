from datetime import date

from app.modules.insights.models.trend_point_response import TrendPointResponse
from app.modules.insights.typing.enums import TrendGrouping
from app.shared.common import WireModel


class TrendsResponse(WireModel):
    group_by: TrendGrouping
    first_day: date
    last_day: date
    executors: list[str]
    points: list[TrendPointResponse]
    total: TrendPointResponse

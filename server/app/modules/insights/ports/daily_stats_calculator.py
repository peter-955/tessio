from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.insights.domains.daily_stats.entity import DailyStats
from app.modules.insights.domains.day_range.entity import DayRange
from app.modules.insights.domains.insights_project.entity import InsightsProject


class DailyStatsCalculator(ABC):
    @abstractmethod
    async def compute(self, project_id: UUID, day_range: DayRange) -> list[DailyStats]: ...

    @abstractmethod
    async def list_snapshot_projects(self) -> list[InsightsProject]: ...

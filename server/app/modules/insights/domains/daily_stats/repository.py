from abc import ABC, abstractmethod
from collections.abc import Sequence
from datetime import date, datetime
from uuid import UUID

from app.modules.insights.domains.daily_stats.entity import DailyStats


class DailyStatsRepository(ABC):
    @abstractmethod
    async def list_between(self, project_id: UUID, first_day: date, last_day: date) -> list[DailyStats]: ...

    @abstractmethod
    async def save_all(self, stats: Sequence[DailyStats], computed_at: datetime) -> None: ...

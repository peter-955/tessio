from abc import ABC, abstractmethod
from datetime import datetime
from uuid import UUID

from app.modules.plans.domains.plan_item.entity import PlanItem


class PlanItemRepository(ABC):
    @abstractmethod
    async def replace(self, plan_id: UUID, items: list[PlanItem], now: datetime) -> None: ...

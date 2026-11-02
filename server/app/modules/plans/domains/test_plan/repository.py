from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.plans.domains.test_plan.entity import TestPlan


class TestPlanRepository(ABC):
    @abstractmethod
    async def find_by_id(self, project_id: UUID, plan_id: UUID) -> TestPlan | None: ...

    @abstractmethod
    async def find_by_id_for_update(self, project_id: UUID, plan_id: UUID) -> TestPlan | None: ...

    @abstractmethod
    async def add(self, plan: TestPlan) -> None: ...

    @abstractmethod
    async def save(self, plan: TestPlan) -> None: ...

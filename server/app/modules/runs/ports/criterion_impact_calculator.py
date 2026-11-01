from abc import ABC, abstractmethod
from uuid import UUID

from app.modules.runs.domains.criterion_impact.entity import CriterionImpact


class CriterionImpactCalculator(ABC):
    @abstractmethod
    async def calculate(self, project_id: UUID, run_id: UUID) -> list[CriterionImpact]: ...

from uuid import UUID

from app.modules.runs.domains.criterion_impact.entity import CriterionImpact
from app.modules.runs.ports.criterion_impact_calculator import CriterionImpactCalculator


class EmptyCriterionImpactCalculator(CriterionImpactCalculator):
    async def calculate(self, project_id: UUID, run_id: UUID) -> list[CriterionImpact]:
        return []

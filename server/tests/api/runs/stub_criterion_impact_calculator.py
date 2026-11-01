from uuid import UUID

from app.modules.runs import CriterionImpact, CriterionImpactCalculator


class StubCriterionImpactCalculator(CriterionImpactCalculator):
    def __init__(self) -> None:
        self.impacts: list[CriterionImpact] = []
        self.calls: list[tuple[UUID, UUID]] = []

    async def calculate(self, project_id: UUID, run_id: UUID) -> list[CriterionImpact]:
        self.calls.append((project_id, run_id))
        return self.impacts

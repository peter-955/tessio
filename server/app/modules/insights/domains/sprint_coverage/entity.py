from app.modules.insights.domains.coverage_count.entity import CoverageCount
from app.modules.insights.domains.sprint_reference.entity import SprintReference
from app.shared.common import Entity


class SprintCoverage(Entity):
    sprint: SprintReference
    story_count: int
    coverage: CoverageCount

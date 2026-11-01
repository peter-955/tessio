from app.modules.insights.domains.coverage_count.entity import CoverageCount
from app.modules.insights.domains.sprint_reference.entity import SprintReference
from app.modules.insights.domains.test_status_counts.entity import TestStatusCounts
from app.shared.common import Entity


class DashboardSummary(Entity):
    sprint: SprintReference | None
    story_count: int
    test_status_counts: TestStatusCounts
    open_gap_count: int
    active_failure_count: int
    coverage: CoverageCount

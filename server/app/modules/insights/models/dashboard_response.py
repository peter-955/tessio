from app.modules.insights.models.coverage_count_response import CoverageCountResponse
from app.modules.insights.models.sprint_reference_response import SprintReferenceResponse
from app.modules.insights.models.test_status_counts_response import TestStatusCountsResponse
from app.shared.common import WireModel


class DashboardResponse(WireModel):
    sprint: SprintReferenceResponse | None
    story_count: int
    test_status_counts: TestStatusCountsResponse
    open_gap_count: int
    active_failure_count: int
    coverage: CoverageCountResponse

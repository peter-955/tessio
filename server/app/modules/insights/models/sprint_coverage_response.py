from app.modules.insights.models.coverage_count_response import CoverageCountResponse
from app.modules.insights.models.sprint_reference_response import SprintReferenceResponse
from app.shared.common import WireModel


class SprintCoverageResponse(WireModel):
    sprint: SprintReferenceResponse
    story_count: int
    coverage: CoverageCountResponse

from uuid import UUID

from app.modules.insights.models.coverage_count_response import CoverageCountResponse
from app.modules.insights.models.run_reference_response import RunReferenceResponse
from app.shared.common import WireModel


class StoryProgressResponse(WireModel):
    story_id: UUID
    jira_key: str
    coverage: CoverageCountResponse
    open_gap_count: int
    active_failure_count: int
    last_run: RunReferenceResponse | None

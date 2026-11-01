from uuid import UUID

from app.modules.insights.models.coverage_count_response import CoverageCountResponse
from app.modules.insights.models.criterion_trace_response import CriterionTraceResponse
from app.modules.insights.models.traced_case_response import TracedCaseResponse
from app.shared.common import WireModel


class TraceabilityResponse(WireModel):
    story_id: UUID
    jira_key: str
    coverage: CoverageCountResponse
    criteria: list[CriterionTraceResponse]
    cases: list[TracedCaseResponse]

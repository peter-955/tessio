from app.modules.insights.models.case_share_counts_response import CaseShareCountsResponse
from app.modules.insights.models.label_coverage_response import LabelCoverageResponse
from app.shared.common import WireModel


class LabelCoverageReportResponse(WireModel):
    labels: list[LabelCoverageResponse]
    unlabelled: CaseShareCountsResponse
    total: CaseShareCountsResponse

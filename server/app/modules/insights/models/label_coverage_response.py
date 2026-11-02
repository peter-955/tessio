from uuid import UUID

from app.modules.insights.models.case_share_counts_response import CaseShareCountsResponse
from app.modules.labels import LabelColor
from app.shared.common import WireModel


class LabelCoverageResponse(WireModel):
    label_id: UUID
    name: str
    color: LabelColor
    counts: CaseShareCountsResponse

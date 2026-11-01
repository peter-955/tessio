from uuid import UUID

from app.modules.insights.models.latest_result_response import LatestResultResponse
from app.shared.common import WireModel


class CaseLatestResultResponse(WireModel):
    case_id: UUID
    code: str
    story_id: UUID
    latest_result: LatestResultResponse | None

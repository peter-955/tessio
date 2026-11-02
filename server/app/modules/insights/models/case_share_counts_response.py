from app.shared.common import WireModel


class CaseShareCountsResponse(WireModel):
    case_count: int
    ready_count: int
    passed_count: int
    ready_share: float | None
    passed_share: float | None

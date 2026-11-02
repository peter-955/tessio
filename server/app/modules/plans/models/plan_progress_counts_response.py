from app.shared.common import WireModel


class PlanProgressCountsResponse(WireModel):
    total: int
    passed: int
    failed: int
    blocked: int
    skipped: int
    not_run: int

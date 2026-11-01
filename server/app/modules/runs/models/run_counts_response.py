from app.shared.common import WireModel


class RunCountsResponse(WireModel):
    total: int
    passed: int
    failed: int
    blocked: int
    skipped: int
    not_reported: int

from app.shared.common import WireModel


class TestStatusCountsResponse(WireModel):
    not_started: int
    ready_for_test: int
    in_test: int
    passed: int
    failed: int

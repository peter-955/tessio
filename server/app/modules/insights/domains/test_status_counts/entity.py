from app.shared.common import Entity


class TestStatusCounts(Entity):
    not_started: int
    ready_for_test: int
    in_test: int
    passed: int
    failed: int

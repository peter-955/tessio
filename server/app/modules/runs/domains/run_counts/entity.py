from app.shared.common import Entity


class RunCounts(Entity):
    total: int
    passed: int
    failed: int
    blocked: int
    skipped: int
    not_reported: int

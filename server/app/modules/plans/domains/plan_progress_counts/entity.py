from app.shared.common import Entity


class PlanProgressCounts(Entity):
    total: int
    passed: int
    failed: int
    blocked: int
    skipped: int
    not_run: int

from app.shared.common import Entity


class CoverageCount(Entity):
    criterion_count: int
    covered_count: int
    passed_count: int
    failed_count: int
    blocked_count: int
    not_run_count: int
    uncovered_count: int

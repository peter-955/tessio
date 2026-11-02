from datetime import date
from uuid import UUID

from app.shared.common import Entity


class DailyStats(Entity):
    project_id: UUID
    day: date
    runs_by_executor: dict[str, int]
    passed_count: int
    failed_count: int
    blocked_count: int
    skipped_count: int
    failures_opened: int
    failures_fixed: int
    fix_seconds_total: int
    gaps_opened: int
    gaps_answered: int
    answer_seconds_total: int
    open_gap_count: int
    median_open_gap_age_seconds: int | None

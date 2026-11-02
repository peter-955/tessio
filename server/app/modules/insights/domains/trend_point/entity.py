from datetime import date

from app.modules.insights.domains.executor_count.entity import ExecutorCount
from app.modules.insights.domains.sprint_reference.entity import SprintReference
from app.shared.common import Entity


class TrendPoint(Entity):
    day: date | None
    sprint: SprintReference | None
    first_day: date
    last_day: date
    run_count: int
    runs_by_executor: list[ExecutorCount]
    passed_count: int
    failed_count: int
    blocked_count: int
    skipped_count: int
    pass_rate: float | None
    failures_opened: int
    failures_fixed: int
    mean_time_to_fix_seconds: int | None
    gaps_opened: int
    gaps_answered: int
    mean_gap_answer_seconds: int | None
    open_gap_count: int
    median_open_gap_age_seconds: int | None

from datetime import date

from app.modules.insights.models.executor_count_response import ExecutorCountResponse
from app.modules.insights.models.sprint_reference_response import SprintReferenceResponse
from app.shared.common import WireModel


class TrendPointResponse(WireModel):
    day: date | None
    sprint: SprintReferenceResponse | None
    first_day: date
    last_day: date
    run_count: int
    runs_by_executor: list[ExecutorCountResponse]
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

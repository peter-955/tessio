from app.modules.insights.domains.day_range.entity import DayRange
from app.modules.insights.domains.token_run.entity import TokenRun
from app.shared.common import Entity


class TokenUsage(Entity):
    day_range: DayRange
    runs: list[TokenRun]
    total_tokens: int
    mean_tokens_per_run: int | None
    mean_tokens_per_case: int | None

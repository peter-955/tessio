from datetime import date

from app.modules.insights.models.token_run_response import TokenRunResponse
from app.shared.common import WireModel


class TokenUsageResponse(WireModel):
    first_day: date
    last_day: date
    runs: list[TokenRunResponse]
    total_tokens: int
    mean_tokens_per_run: int | None
    mean_tokens_per_case: int | None

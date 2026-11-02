from datetime import UTC, date, datetime

from app.modules.insights.domains.token_usage.entity import TokenUsage
from app.modules.insights.ports.token_usage_reader import TokenUsageReader
from app.modules.insights.typing.constants import MAX_TOKEN_RUNS
from app.modules.insights.utils.day_bounds import resolve_range_bounds
from app.modules.insights.utils.day_range import resolve_day_range
from app.modules.insights.utils.trend_points import compute_mean
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetTokenUsageUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        token_usage_reader: TokenUsageReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._token_usage_reader = token_usage_reader

    async def execute(
        self, actor: Actor, project_key: str, first_day: date | None, last_day: date | None
    ) -> TokenUsage:
        day_range = resolve_day_range(first_day, last_day, datetime.now(UTC).date())
        start_at, end_at = resolve_range_bounds(day_range)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            runs = await self._token_usage_reader.list_token_runs(access.project_id, start_at, end_at, MAX_TOKEN_RUNS)
        total_tokens = sum(run.total_tokens for run in runs)
        return TokenUsage(
            day_range=day_range,
            runs=runs,
            total_tokens=total_tokens,
            mean_tokens_per_run=compute_mean(total_tokens, len(runs)),
            mean_tokens_per_case=compute_mean(total_tokens, sum(run.case_count for run in runs)),
        )

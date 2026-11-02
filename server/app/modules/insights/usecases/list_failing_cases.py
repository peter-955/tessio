from datetime import UTC, date, datetime

from app.modules.insights.domains.failing_case.entity import FailingCase
from app.modules.insights.ports.quality_reader import QualityReader
from app.modules.insights.utils.day_bounds import resolve_range_bounds
from app.modules.insights.utils.day_range import resolve_day_range
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListFailingCasesUseCase:
    def __init__(
        self, transaction: Transaction, project_access_resolver: ProjectAccessResolver, quality_reader: QualityReader
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._quality_reader = quality_reader

    async def execute(
        self, actor: Actor, project_key: str, first_day: date | None, last_day: date | None, limit: int
    ) -> list[FailingCase]:
        day_range = resolve_day_range(first_day, last_day, datetime.now(UTC).date())
        start_at, end_at = resolve_range_bounds(day_range)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            return await self._quality_reader.list_failing_cases(access.project_id, start_at, end_at, limit)

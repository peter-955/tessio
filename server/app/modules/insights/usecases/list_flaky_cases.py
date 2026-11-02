from app.modules.insights.domains.flaky_case.entity import FlakyCase
from app.modules.insights.ports.quality_reader import QualityReader
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListFlakyCasesUseCase:
    def __init__(
        self, transaction: Transaction, project_access_resolver: ProjectAccessResolver, quality_reader: QualityReader
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._quality_reader = quality_reader

    async def execute(self, actor: Actor, project_key: str, limit: int) -> list[FlakyCase]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            return await self._quality_reader.list_flaky_cases(access.project_id, limit)

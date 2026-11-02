from app.modules.insights.domains.label_coverage_report.entity import LabelCoverageReport
from app.modules.insights.ports.quality_reader import QualityReader
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetLabelCoverageUseCase:
    def __init__(
        self, transaction: Transaction, project_access_resolver: ProjectAccessResolver, quality_reader: QualityReader
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._quality_reader = quality_reader

    async def execute(self, actor: Actor, project_key: str) -> LabelCoverageReport:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            return await self._quality_reader.get_label_coverage(access.project_id)

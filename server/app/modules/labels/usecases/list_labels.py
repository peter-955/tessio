from app.modules.labels.domains.label.repository import LabelRepository
from app.modules.labels.domains.label_summary.entity import LabelSummary
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListLabelsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        label_repository: LabelRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._label_repository = label_repository

    async def execute(self, actor: Actor, project_key: str) -> list[LabelSummary]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.TEST_CASE_VIEW)
            return await self._label_repository.list_summaries(access.project_id)

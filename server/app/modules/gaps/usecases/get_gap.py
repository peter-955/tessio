from uuid import UUID

from app.modules.gaps.domains.gap.repository import GapRepository
from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.errors import GapNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetGapUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        gap_repository: GapRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._gap_repository = gap_repository

    async def execute(self, actor: Actor, project_key: str, gap_id: UUID) -> GapView:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.GAP_VIEW)
            view = await self._gap_repository.find_view(access.project_id, gap_id)
        if view is None:
            raise GapNotFoundError
        return view

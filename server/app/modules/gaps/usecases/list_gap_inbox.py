from app.modules.gaps.domains.gap.repository import GapRepository
from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.typing.constants import MAX_INBOX_SIZE
from app.shared.common import Transaction
from app.shared.permissions import Actor, ProjectAccessResolver


class ListGapInboxUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        gap_repository: GapRepository,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._gap_repository = gap_repository

    async def execute(self, actor: Actor, is_including_resolved: bool) -> list[GapView]:
        async with self._transaction.begin():
            project_ids = await self._project_access_resolver.list_visible_project_ids(actor)
            views = await self._gap_repository.list_inbox_views(
                actor.user_id, project_ids, is_including_resolved, MAX_INBOX_SIZE
            )
        return views

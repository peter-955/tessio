from uuid import UUID

from app.modules.gaps.domains.gap.repository import GapRepository
from app.modules.gaps.domains.gap_filter.entity import GapFilter
from app.modules.gaps.domains.gap_recipient.entity import GapRecipient
from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.ports.gap_target_reader import GapTargetReader
from app.modules.gaps.typing.enums import GapStatus
from app.modules.stories import StoryNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListGapsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        gap_repository: GapRepository,
        gap_target_reader: GapTargetReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._gap_repository = gap_repository
        self._gap_target_reader = gap_target_reader

    async def execute(
        self, actor: Actor, project_key: str, story_key: str | None, status: GapStatus | None, is_mine: bool
    ) -> list[GapView]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.GAP_VIEW)
            story_id: UUID | None = None
            if story_key is not None:
                story = await self._gap_target_reader.find_story(access.project_id, story_key)
                if story is None:
                    raise StoryNotFoundError
                story_id = story.id
            assigned_to = GapRecipient(user_id=actor.user_id, role=access.role) if is_mine else None
            views = await self._gap_repository.list_views(
                access.project_id, GapFilter(story_id=story_id, status=status, assigned_to=assigned_to)
            )
        return views

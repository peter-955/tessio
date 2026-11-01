from app.modules.gaps.domains.gap.repository import GapRepository
from app.modules.gaps.domains.gap_filter.entity import GapFilter
from app.modules.gaps.domains.raised_gaps.entity import RaisedGaps
from app.modules.gaps.ports.gap_target_reader import GapTargetReader
from app.modules.gaps.typing.enums import GapStatus
from app.modules.stories import StoryNotFoundError
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, ProjectNotFoundError, require


class GetOpenGapsUseCase:
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

    async def execute_in_token_project(self, actor: Actor, story_key: str) -> RaisedGaps:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            require(access, Capability.GAP_VIEW)
            story = await self._gap_target_reader.find_story(access.project_id, story_key)
            if story is None:
                raise StoryNotFoundError
            open_views = await self._gap_repository.list_views(
                access.project_id, GapFilter(story_id=story.id, status=GapStatus.OPEN)
            )
        return RaisedGaps(gaps=open_views, open_gap_count=len(open_views))

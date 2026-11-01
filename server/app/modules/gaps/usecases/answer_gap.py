from datetime import UTC, datetime
from uuid import UUID

from app.modules.gaps.domains.gap.repository import GapRepository
from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.errors import GapNotFoundError, GapNotOpenError
from app.modules.gaps.typing.enums import GapStatus
from app.modules.gaps.utils.gap_notification import build_gap_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class AnswerGapUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        gap_repository: GapRepository,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._gap_repository = gap_repository
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, gap_id: UUID, answer: str) -> GapView:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.GAP_ANSWER)
            gap = await self._gap_repository.find_for_update(access.project_id, gap_id)
            if gap is None:
                raise GapNotFoundError
            if not gap.is_open:
                raise GapNotOpenError
            await self._gap_repository.save(
                gap.model_copy(
                    update={
                        "answer": answer,
                        "answered_by": actor.user_id,
                        "answered_at": now,
                        "status": GapStatus.RESOLVED,
                    }
                )
            )
            view = await self._gap_repository.find_view(access.project_id, gap.id)
            if view is None:
                raise GapNotFoundError
        await self._live_event_publisher.publish(build_gap_changed_event(view.gap))
        return view

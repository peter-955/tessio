from datetime import UTC, datetime
from uuid import UUID

from app.modules.gaps.domains.gap.entity import Gap
from app.modules.gaps.domains.gap.repository import GapRepository
from app.modules.gaps.domains.gap_route.entity import GapRoute
from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.errors import GapNotFoundError, GapNotResolvedError
from app.modules.gaps.ports.gap_assignee_directory import GapAssigneeDirectory
from app.modules.gaps.typing.constants import FALLBACK_ROLE, REOPENING_ROLES
from app.modules.gaps.typing.enums import GapStatus
from app.modules.gaps.utils.gap_notification import (
    build_gap_assigned_payload,
    build_gap_changed_event,
    list_recipient_ids,
    list_recipient_roles,
)
from app.modules.gaps.utils.gap_route import choose_gap_route, resolve_routed_role
from app.modules.notifications import SendNotificationUseCase
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import (
    Actor,
    Capability,
    PermissionDeniedError,
    ProjectAccessResolver,
    ProjectRole,
    require,
)


class ReopenGapUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        gap_repository: GapRepository,
        gap_assignee_directory: GapAssigneeDirectory,
        send_notification: SendNotificationUseCase,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._gap_repository = gap_repository
        self._gap_assignee_directory = gap_assignee_directory
        self._send_notification = send_notification
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, gap_id: UUID) -> GapView:
        now = datetime.now(UTC)
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.GAP_RAISE)
            gap = await self._gap_repository.find_for_update(access.project_id, gap_id)
            if gap is None:
                raise GapNotFoundError
            if gap.raised_by != actor.user_id and access.role not in REOPENING_ROLES:
                raise PermissionDeniedError
            if gap.is_open:
                raise GapNotResolvedError
            route = await self._find_route(gap)
            await self._gap_repository.save(
                gap.model_copy(
                    update={
                        "status": GapStatus.OPEN,
                        "reopened_by": actor.user_id,
                        "reopened_at": now,
                        "assignee_id": route.assignee_id,
                        "assignee_role": route.assignee_role,
                    }
                )
            )
            view = await self._gap_repository.find_view(access.project_id, gap.id)
            if view is None:
                raise GapNotFoundError
        await self._send_notification.execute(
            view.gap.project_id,
            build_gap_assigned_payload(view),
            actor_id=actor.user_id,
            recipient_ids=list_recipient_ids(view.gap),
            recipient_roles=list_recipient_roles(view.gap),
        )
        await self._live_event_publisher.publish(build_gap_changed_event(view.gap))
        return view

    async def _find_route(self, gap: Gap) -> GapRoute:
        current_route = GapRoute(assignee_id=gap.assignee_id, assignee_role=gap.assignee_role)
        if gap.assignee_id is None:
            return current_route
        role = await self._gap_assignee_directory.find_active_member_role(gap.project_id, gap.assignee_id)
        if role is not None and role is not ProjectRole.VIEWER:
            return current_route
        routed_role = resolve_routed_role(gap.type, gap.data_scope)
        active_member_ids = await self._gap_assignee_directory.list_active_member_ids(
            gap.project_id, frozenset({routed_role, FALLBACK_ROLE})
        )
        return choose_gap_route(routed_role, active_member_ids)

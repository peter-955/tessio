from uuid import UUID

from app.modules.gaps.domains.gap.repository import GapRepository
from app.modules.gaps.domains.gap_route.entity import GapRoute
from app.modules.gaps.domains.gap_view.entity import GapView
from app.modules.gaps.errors import AssigneeNotActiveMemberError, GapNotFoundError, GapNotOpenError
from app.modules.gaps.ports.gap_assignee_directory import GapAssigneeDirectory
from app.modules.gaps.utils.gap_notification import (
    build_gap_assigned_payload,
    build_gap_changed_event,
    list_recipient_ids,
    list_recipient_roles,
)
from app.modules.notifications import SendNotificationUseCase
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import (
    Actor,
    Capability,
    ProjectAccess,
    ProjectAccessResolver,
    ProjectNotFoundError,
    ProjectRole,
    require,
)


class ReassignGapUseCase:
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

    async def execute(self, actor: Actor, project_key: str, gap_id: UUID, route: GapRoute) -> GapView:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            view = await self._reassign(access, gap_id, route)
        await self._announce(actor, view)
        return view

    async def execute_in_token_project(self, actor: Actor, gap_id: UUID, route: GapRoute) -> GapView:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            view = await self._reassign(access, gap_id, route)
        await self._announce(actor, view)
        return view

    async def _reassign(self, access: ProjectAccess, gap_id: UUID, route: GapRoute) -> GapView:
        require(access, Capability.GAP_REASSIGN)
        gap = await self._gap_repository.find_for_update(access.project_id, gap_id)
        if gap is None:
            raise GapNotFoundError
        if not gap.is_open:
            raise GapNotOpenError
        if route.assignee_id is not None:
            role = await self._gap_assignee_directory.find_active_member_role(access.project_id, route.assignee_id)
            if role is None or role is ProjectRole.VIEWER:
                raise AssigneeNotActiveMemberError
            assigned_route = GapRoute(assignee_id=route.assignee_id, assignee_role=None)
        else:
            assigned_route = GapRoute(assignee_id=None, assignee_role=route.assignee_role)
        await self._gap_repository.save(
            gap.model_copy(
                update={"assignee_id": assigned_route.assignee_id, "assignee_role": assigned_route.assignee_role}
            )
        )
        view = await self._gap_repository.find_view(access.project_id, gap.id)
        if view is None:
            raise GapNotFoundError
        return view

    async def _announce(self, actor: Actor, view: GapView) -> None:
        await self._send_notification.execute(
            view.gap.project_id,
            build_gap_assigned_payload(view),
            actor_id=actor.user_id,
            recipient_ids=list_recipient_ids(view.gap),
            recipient_roles=list_recipient_roles(view.gap),
        )
        await self._live_event_publisher.publish(build_gap_changed_event(view.gap))

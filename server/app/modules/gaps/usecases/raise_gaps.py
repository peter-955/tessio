from collections.abc import Mapping, Sequence
from datetime import UTC, datetime
from uuid import UUID, uuid7

from app.modules.gaps.domains.gap.entity import Gap
from app.modules.gaps.domains.gap.repository import GapRepository
from app.modules.gaps.domains.gap_draft.entity import GapDraft
from app.modules.gaps.domains.gap_filter.entity import GapFilter
from app.modules.gaps.domains.gap_route.entity import GapRoute
from app.modules.gaps.domains.raised_gaps.entity import RaisedGaps
from app.modules.gaps.errors import AssigneeNotActiveMemberError, UnknownGapTargetError
from app.modules.gaps.ports.gap_assignee_directory import GapAssigneeDirectory
from app.modules.gaps.ports.gap_target_reader import GapTargetReader
from app.modules.gaps.typing.constants import FALLBACK_ROLE
from app.modules.gaps.typing.enums import GapStatus, GapTargetType, GapType
from app.modules.gaps.utils.gap_notification import (
    build_gap_assigned_payload,
    build_gap_changed_event,
    build_gap_raised_event,
    list_recipient_ids,
    list_recipient_roles,
)
from app.modules.gaps.utils.gap_route import choose_gap_route, resolve_routed_role
from app.modules.notifications import SendNotificationUseCase
from app.modules.stories import StoryNotFoundError
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


class RaiseGapsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        gap_repository: GapRepository,
        gap_target_reader: GapTargetReader,
        gap_assignee_directory: GapAssigneeDirectory,
        send_notification: SendNotificationUseCase,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._gap_repository = gap_repository
        self._gap_target_reader = gap_target_reader
        self._gap_assignee_directory = gap_assignee_directory
        self._send_notification = send_notification
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, story_key: str, drafts: Sequence[GapDraft]) -> RaisedGaps:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            raised_gaps = await self._raise(actor, access, story_key, drafts)
        await self._announce(actor, raised_gaps)
        return raised_gaps

    async def execute_in_token_project(self, actor: Actor, story_key: str, drafts: Sequence[GapDraft]) -> RaisedGaps:
        if actor.token_project_id is None:
            raise ProjectNotFoundError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve_by_id(actor, actor.token_project_id)
            raised_gaps = await self._raise(actor, access, story_key, drafts)
        await self._announce(actor, raised_gaps)
        return raised_gaps

    async def _raise(
        self, actor: Actor, access: ProjectAccess, story_key: str, drafts: Sequence[GapDraft]
    ) -> RaisedGaps:
        require(access, Capability.GAP_RAISE)
        story = await self._gap_target_reader.find_story(access.project_id, story_key)
        if story is None:
            raise StoryNotFoundError
        now = datetime.now(UTC)
        kept_drafts = [self._keep_data_scope(draft) for draft in drafts]
        routed_roles = frozenset(
            resolve_routed_role(draft.type, draft.data_scope) for draft in kept_drafts if draft.assignee_id is None
        )
        active_member_ids: Mapping[ProjectRole, list[UUID]] = (
            await self._gap_assignee_directory.list_active_member_ids(access.project_id, routed_roles | {FALLBACK_ROLE})
            if routed_roles
            else {}
        )
        gaps: list[Gap] = []
        for draft in kept_drafts:
            target_id = await self._resolve_target_id(story.id, draft)
            route = await self._route(access.project_id, draft, active_member_ids)
            gaps.append(
                Gap(
                    id=uuid7(),
                    project_id=access.project_id,
                    story_id=story.id,
                    target_type=draft.target_type,
                    target_id=target_id,
                    type=draft.type,
                    data_scope=draft.data_scope,
                    severity=draft.severity,
                    question=draft.question,
                    status=GapStatus.OPEN,
                    assignee_id=route.assignee_id,
                    assignee_role=route.assignee_role,
                    raised_by=actor.user_id,
                    raised_via_token_id=actor.api_token_id,
                    answer=None,
                    answered_by=None,
                    answered_at=None,
                    answered_via_token_id=None,
                    reopened_by=None,
                    reopened_at=None,
                    created_at=now,
                )
            )
        await self._gap_repository.add_all(gaps)
        open_gap_count = await self._gap_repository.count_open(story.id)
        open_views = await self._gap_repository.list_views(
            access.project_id, GapFilter(story_id=story.id, status=GapStatus.OPEN)
        )
        views_by_id = {view.gap.id: view for view in open_views}
        return RaisedGaps(gaps=[views_by_id[gap.id] for gap in gaps], open_gap_count=open_gap_count)

    @staticmethod
    def _keep_data_scope(draft: GapDraft) -> GapDraft:
        if draft.type is GapType.MISSING_TEST_DATA or draft.data_scope is None:
            return draft
        return draft.model_copy(update={"data_scope": None})

    async def _resolve_target_id(self, story_id: UUID, draft: GapDraft) -> UUID | None:
        if draft.target_type is GapTargetType.STORY:
            return None
        if not draft.target_ref:
            raise UnknownGapTargetError("")
        if draft.target_type is GapTargetType.CRITERION:
            target_id = await self._gap_target_reader.find_criterion_id(story_id, draft.target_ref)
        else:
            target_id = await self._gap_target_reader.find_test_case_id(story_id, draft.target_ref)
        if target_id is None:
            raise UnknownGapTargetError(draft.target_ref)
        return target_id

    async def _route(
        self, project_id: UUID, draft: GapDraft, active_member_ids: Mapping[ProjectRole, list[UUID]]
    ) -> GapRoute:
        if draft.assignee_id is None:
            return choose_gap_route(resolve_routed_role(draft.type, draft.data_scope), active_member_ids)
        role = await self._gap_assignee_directory.find_active_member_role(project_id, draft.assignee_id)
        if role is None or role is ProjectRole.VIEWER:
            raise AssigneeNotActiveMemberError
        return GapRoute(assignee_id=draft.assignee_id, assignee_role=None)

    async def _announce(self, actor: Actor, raised_gaps: RaisedGaps) -> None:
        for view in raised_gaps.gaps:
            await self._send_notification.execute(
                view.gap.project_id,
                build_gap_assigned_payload(view),
                actor_id=actor.user_id,
                recipient_ids=list_recipient_ids(view.gap),
                recipient_roles=list_recipient_roles(view.gap),
            )
            await self._live_event_publisher.publish(build_gap_changed_event(view.gap))
            await self._live_event_publisher.publish(build_gap_raised_event(view.gap))

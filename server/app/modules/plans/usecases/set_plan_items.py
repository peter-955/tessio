from datetime import UTC, datetime
from uuid import UUID

from app.modules.plans.domains.plan_detail.entity import PlanDetail
from app.modules.plans.domains.plan_item.entity import PlanItem
from app.modules.plans.domains.plan_item.repository import PlanItemRepository
from app.modules.plans.domains.test_plan.repository import TestPlanRepository
from app.modules.plans.errors import DuplicatePlanItemError, TooManyPlanItemsError, UnknownPlanItemError
from app.modules.plans.ports.plan_reference_reader import PlanReferenceReader
from app.modules.plans.ports.plan_view_reader import PlanViewReader
from app.modules.plans.typing.constants import MAX_PLAN_ITEMS
from app.modules.plans.utils.plan_detail import load_plan_detail, lock_open_plan
from app.modules.plans.utils.plan_event import build_plan_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class SetPlanItemsUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_plan_repository: TestPlanRepository,
        plan_item_repository: PlanItemRepository,
        plan_reference_reader: PlanReferenceReader,
        plan_view_reader: PlanViewReader,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_plan_repository = test_plan_repository
        self._plan_item_repository = plan_item_repository
        self._plan_reference_reader = plan_reference_reader
        self._plan_view_reader = plan_view_reader
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, plan_id: UUID, items: list[PlanItem]) -> PlanDetail:
        suite_ids = [item.test_suite_id for item in items if item.test_suite_id is not None]
        story_ids = [item.story_id for item in items if item.story_id is not None]
        if len(set(suite_ids)) != len(suite_ids) or len(set(story_ids)) != len(story_ids):
            raise DuplicatePlanItemError
        if len(items) > MAX_PLAN_ITEMS:
            raise TooManyPlanItemsError
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.PLAN_EDIT)
            plan = await lock_open_plan(self._test_plan_repository, access.project_id, plan_id)
            known_suite_ids = await self._plan_reference_reader.list_project_suite_ids(access.project_id, suite_ids)
            known_story_ids = await self._plan_reference_reader.list_project_story_ids(access.project_id, story_ids)
            if len(known_suite_ids) != len(suite_ids) or len(known_story_ids) != len(story_ids):
                raise UnknownPlanItemError
            await self._plan_item_repository.replace(plan.id, items, datetime.now(UTC))
            detail = await load_plan_detail(self._plan_view_reader, plan)
        await self._live_event_publisher.publish(build_plan_changed_event(plan))
        return detail

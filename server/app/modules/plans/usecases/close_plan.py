from datetime import UTC, datetime
from uuid import UUID

from app.modules.plans.domains.plan_detail.entity import PlanDetail
from app.modules.plans.domains.test_plan.repository import TestPlanRepository
from app.modules.plans.errors import PlanNotOpenError
from app.modules.plans.ports.plan_view_reader import PlanViewReader
from app.modules.plans.typing.enums import PlanStatus
from app.modules.plans.utils.plan_detail import load_plan_detail, lock_plan
from app.modules.plans.utils.plan_event import build_plan_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ClosePlanUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_plan_repository: TestPlanRepository,
        plan_view_reader: PlanViewReader,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_plan_repository = test_plan_repository
        self._plan_view_reader = plan_view_reader
        self._live_event_publisher = live_event_publisher

    async def execute(self, actor: Actor, project_key: str, plan_id: UUID) -> PlanDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.PLAN_EDIT)
            plan = await lock_plan(self._test_plan_repository, access.project_id, plan_id)
            if plan.status is PlanStatus.CLOSED:
                raise PlanNotOpenError(plan.status)
            closed = plan.model_copy(
                update={"status": PlanStatus.CLOSED, "closed_by": actor.user_id, "closed_at": datetime.now(UTC)}
            )
            await self._test_plan_repository.save(closed)
            detail = await load_plan_detail(self._plan_view_reader, closed)
        await self._live_event_publisher.publish(build_plan_changed_event(closed))
        return detail

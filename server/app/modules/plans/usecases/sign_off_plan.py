from datetime import UTC, datetime
from uuid import UUID

from app.modules.plans.domains.plan_detail.entity import PlanDetail
from app.modules.plans.domains.test_plan.repository import TestPlanRepository
from app.modules.plans.errors import PlanFailuresActiveError
from app.modules.plans.ports.plan_view_reader import PlanViewReader
from app.modules.plans.typing.enums import PlanStatus
from app.modules.plans.utils.plan_detail import load_plan_detail, lock_open_plan
from app.modules.plans.utils.plan_event import build_plan_changed_event, build_plan_signed_off_event
from app.modules.plans.utils.plan_progress import list_active_plan_failures
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class SignOffPlanUseCase:
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
            require(access, Capability.PLAN_SIGN_OFF)
            plan = await lock_open_plan(self._test_plan_repository, access.project_id, plan_id)
            active_failures = await list_active_plan_failures(self._plan_view_reader, plan)
            if active_failures:
                raise PlanFailuresActiveError(len(active_failures))
            signed_off = plan.model_copy(
                update={
                    "status": PlanStatus.SIGNED_OFF,
                    "signed_off_by": actor.user_id,
                    "signed_off_at": datetime.now(UTC),
                }
            )
            await self._test_plan_repository.save(signed_off)
            detail = await load_plan_detail(self._plan_view_reader, signed_off)
        await self._live_event_publisher.publish(build_plan_changed_event(signed_off))
        await self._live_event_publisher.publish(build_plan_signed_off_event(signed_off))
        return detail

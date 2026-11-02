from datetime import UTC, date, datetime
from uuid import UUID, uuid7

from app.modules.plans.domains.plan_detail.entity import PlanDetail
from app.modules.plans.domains.test_plan.entity import TestPlan
from app.modules.plans.domains.test_plan.repository import TestPlanRepository
from app.modules.plans.errors import UnknownPlanEnvironmentError
from app.modules.plans.ports.plan_reference_reader import PlanReferenceReader
from app.modules.plans.ports.plan_view_reader import PlanViewReader
from app.modules.plans.typing.enums import PlanStatus
from app.modules.plans.utils.plan_detail import load_plan_detail
from app.modules.plans.utils.plan_event import build_plan_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class CreatePlanUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_plan_repository: TestPlanRepository,
        plan_reference_reader: PlanReferenceReader,
        plan_view_reader: PlanViewReader,
        live_event_publisher: LiveEventPublisher,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_plan_repository = test_plan_repository
        self._plan_reference_reader = plan_reference_reader
        self._plan_view_reader = plan_view_reader
        self._live_event_publisher = live_event_publisher

    async def execute(
        self,
        actor: Actor,
        project_key: str,
        name: str,
        description: str | None,
        target_date: date | None,
        environment_id: UUID | None,
    ) -> PlanDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.PLAN_EDIT)
            if environment_id is not None and not await self._plan_reference_reader.is_active_environment(
                access.project_id, environment_id
            ):
                raise UnknownPlanEnvironmentError
            plan = TestPlan(
                id=uuid7(),
                project_id=access.project_id,
                name=name,
                description=description or None,
                target_date=target_date,
                environment_id=environment_id,
                status=PlanStatus.OPEN,
                signed_off_by=None,
                signed_off_at=None,
                closed_by=None,
                closed_at=None,
                created_by=actor.user_id,
                created_at=datetime.now(UTC),
            )
            await self._test_plan_repository.add(plan)
            detail = await load_plan_detail(self._plan_view_reader, plan)
        await self._live_event_publisher.publish(build_plan_changed_event(plan))
        return detail

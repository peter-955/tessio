from uuid import UUID

from app.modules.plans.domains.plan_detail.entity import PlanDetail
from app.modules.plans.domains.plan_patch.entity import PlanPatch
from app.modules.plans.domains.test_plan.repository import TestPlanRepository
from app.modules.plans.errors import UnknownPlanEnvironmentError
from app.modules.plans.ports.plan_reference_reader import PlanReferenceReader
from app.modules.plans.ports.plan_view_reader import PlanViewReader
from app.modules.plans.utils.plan_detail import load_plan_detail, lock_open_plan
from app.modules.plans.utils.plan_event import build_plan_changed_event
from app.shared.common import Transaction
from app.shared.events import LiveEventPublisher
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class UpdatePlanUseCase:
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

    async def execute(self, actor: Actor, project_key: str, plan_id: UUID, patch: PlanPatch) -> PlanDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.PLAN_EDIT)
            plan = await lock_open_plan(self._test_plan_repository, access.project_id, plan_id)
            changes: dict[str, object] = {}
            if patch.name is not None and patch.name != plan.name:
                changes["name"] = patch.name
            if patch.is_changing_description and (patch.description or None) != plan.description:
                changes["description"] = patch.description or None
            if patch.is_changing_target_date and patch.target_date != plan.target_date:
                changes["target_date"] = patch.target_date
            if patch.is_changing_environment and patch.environment_id != plan.environment_id:
                if patch.environment_id is not None and not await self._plan_reference_reader.is_active_environment(
                    access.project_id, patch.environment_id
                ):
                    raise UnknownPlanEnvironmentError
                changes["environment_id"] = patch.environment_id
            updated = plan.model_copy(update=changes)
            if changes:
                await self._test_plan_repository.save(updated)
            detail = await load_plan_detail(self._plan_view_reader, updated)
        if changes:
            await self._live_event_publisher.publish(build_plan_changed_event(updated))
        return detail

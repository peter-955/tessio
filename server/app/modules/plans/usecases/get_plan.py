from uuid import UUID

from app.modules.plans.domains.plan_detail.entity import PlanDetail
from app.modules.plans.domains.test_plan.repository import TestPlanRepository
from app.modules.plans.errors import PlanNotFoundError
from app.modules.plans.ports.plan_view_reader import PlanViewReader
from app.modules.plans.utils.plan_detail import load_plan_detail
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class GetPlanUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        test_plan_repository: TestPlanRepository,
        plan_view_reader: PlanViewReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._test_plan_repository = test_plan_repository
        self._plan_view_reader = plan_view_reader

    async def execute(self, actor: Actor, project_key: str, plan_id: UUID) -> PlanDetail:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            plan = await self._test_plan_repository.find_by_id(access.project_id, plan_id)
            if plan is None:
                raise PlanNotFoundError
            detail = await load_plan_detail(self._plan_view_reader, plan)
        return detail

from app.modules.plans.domains.plan_summary.entity import PlanSummary
from app.modules.plans.ports.plan_view_reader import PlanViewReader
from app.modules.plans.typing.enums import PlanStatus
from app.modules.plans.utils.plan_progress import load_plan_counts
from app.shared.common import Transaction
from app.shared.permissions import Actor, Capability, ProjectAccessResolver, require


class ListPlansUseCase:
    def __init__(
        self,
        transaction: Transaction,
        project_access_resolver: ProjectAccessResolver,
        plan_view_reader: PlanViewReader,
    ) -> None:
        self._transaction = transaction
        self._project_access_resolver = project_access_resolver
        self._plan_view_reader = plan_view_reader

    async def execute(self, actor: Actor, project_key: str, status: PlanStatus | None) -> list[PlanSummary]:
        async with self._transaction.begin():
            access = await self._project_access_resolver.resolve(actor, project_key)
            require(access, Capability.REPORT_VIEW)
            plans = await self._plan_view_reader.list_plans(access.project_id, status)
            item_counts = await self._plan_view_reader.count_items([plan.id for plan in plans])
            environment_names = await self._plan_view_reader.map_environment_names(
                access.project_id, {plan.environment_id for plan in plans if plan.environment_id is not None}
            )
            summaries = [
                PlanSummary(
                    plan=plan,
                    environment_name=environment_names.get(plan.environment_id) if plan.environment_id else None,
                    item_count=item_counts.get(plan.id, 0),
                    counts=await load_plan_counts(self._plan_view_reader, plan),
                )
                for plan in plans
            ]
        return summaries

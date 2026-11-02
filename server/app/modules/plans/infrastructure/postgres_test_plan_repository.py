from uuid import UUID

from sqlalchemy import select

from app.modules.plans.domains.test_plan.entity import TestPlan
from app.modules.plans.domains.test_plan.repository import TestPlanRepository
from app.modules.plans.infrastructure.test_plan_table import TestPlanTable
from app.shared.postgres import Database


class PostgresTestPlanRepository(TestPlanRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_id(self, project_id: UUID, plan_id: UUID) -> TestPlan | None:
        row = await self._database.get_current_session().scalar(
            select(TestPlanTable)
            .where(TestPlanTable.project_id == project_id, TestPlanTable.id == plan_id)
            .execution_options(populate_existing=True)
        )
        return None if row is None else TestPlan.model_validate(row)

    async def find_by_id_for_update(self, project_id: UUID, plan_id: UUID) -> TestPlan | None:
        row = await self._database.get_current_session().scalar(
            select(TestPlanTable)
            .where(TestPlanTable.project_id == project_id, TestPlanTable.id == plan_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else TestPlan.model_validate(row)

    async def add(self, plan: TestPlan) -> None:
        session = self._database.get_current_session()
        session.add(TestPlanTable(**plan.model_dump()))
        await session.flush()

    async def save(self, plan: TestPlan) -> None:
        session = self._database.get_current_session()
        await session.merge(TestPlanTable(**plan.model_dump()))
        await session.flush()

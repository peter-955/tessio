from datetime import datetime
from uuid import UUID, uuid7

from sqlalchemy import delete, insert

from app.modules.plans.domains.plan_item.entity import PlanItem
from app.modules.plans.domains.plan_item.repository import PlanItemRepository
from app.modules.plans.infrastructure.test_plan_item_table import TestPlanItemTable
from app.shared.postgres import Database


class PostgresPlanItemRepository(PlanItemRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def replace(self, plan_id: UUID, items: list[PlanItem], now: datetime) -> None:
        session = self._database.get_current_session()
        await session.execute(delete(TestPlanItemTable).where(TestPlanItemTable.test_plan_id == plan_id))
        if not items:
            return
        await session.execute(
            insert(TestPlanItemTable),
            [
                {
                    "id": uuid7(),
                    "test_plan_id": plan_id,
                    "test_suite_id": item.test_suite_id,
                    "story_id": item.story_id,
                    "position": position,
                    "created_at": now,
                }
                for position, item in enumerate(items, start=1)
            ],
        )

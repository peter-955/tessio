from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, insert, select

from app.modules.suites.domains.suite_case.repository import SuiteCaseRepository
from app.modules.suites.infrastructure.test_suite_case_table import TestSuiteCaseTable
from app.shared.postgres import Database


class PostgresSuiteCaseRepository(SuiteCaseRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_case_ids(self, suite_id: UUID) -> list[UUID]:
        case_ids = await self._database.get_current_session().scalars(
            select(TestSuiteCaseTable.test_case_id)
            .where(TestSuiteCaseTable.test_suite_id == suite_id)
            .order_by(TestSuiteCaseTable.position)
        )
        return list(case_ids)

    async def replace(self, suite_id: UUID, test_case_ids: list[UUID], now: datetime) -> None:
        session = self._database.get_current_session()
        await session.execute(delete(TestSuiteCaseTable).where(TestSuiteCaseTable.test_suite_id == suite_id))
        if not test_case_ids:
            return
        await session.execute(
            insert(TestSuiteCaseTable),
            [
                {"test_suite_id": suite_id, "test_case_id": test_case_id, "position": position, "created_at": now}
                for position, test_case_id in enumerate(test_case_ids, start=1)
            ],
        )

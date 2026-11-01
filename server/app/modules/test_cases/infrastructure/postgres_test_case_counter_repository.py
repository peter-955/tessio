from datetime import datetime
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert

from app.modules.test_cases.domains.test_case_counter.repository import TestCaseCounterRepository
from app.modules.test_cases.infrastructure.test_case_counter_table import TestCaseCounterTable
from app.shared.postgres import Database


class PostgresTestCaseCounterRepository(TestCaseCounterRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def allocate_number(self, project_id: UUID, now: datetime) -> int:
        number = await self._database.get_current_session().scalar(
            insert(TestCaseCounterTable)
            .values(project_id=project_id, last_number=1, created_at=now)
            .on_conflict_do_update(
                index_elements=["project_id"], set_={"last_number": TestCaseCounterTable.last_number + 1}
            )
            .returning(TestCaseCounterTable.last_number)
        )
        if not isinstance(number, int):
            raise RuntimeError("Test case counter upsert returned no number")
        return number

from uuid import UUID

from sqlalchemy import select, update

from app.modules.test_cases.domains.test_case.entity import TestCase
from app.modules.test_cases.domains.test_case_quality.repository import TestCaseQualityRepository
from app.modules.test_cases.infrastructure.test_case_table import TestCaseTable
from app.shared.postgres import Database


class PostgresTestCaseQualityRepository(TestCaseQualityRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_id_for_update(self, test_case_id: UUID) -> TestCase | None:
        row = await self._database.get_current_session().scalar(
            select(TestCaseTable)
            .where(TestCaseTable.id == test_case_id, TestCaseTable.current_version_id.is_not(None))
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else TestCase.model_validate(row)

    async def list_case_ids(self) -> list[UUID]:
        rows = await self._database.get_current_session().scalars(
            select(TestCaseTable.id).order_by(TestCaseTable.project_id, TestCaseTable.number)
        )
        return list(rows)

    async def save(self, test_case: TestCase) -> None:
        await self._database.get_current_session().execute(
            update(TestCaseTable)
            .where(TestCaseTable.id == test_case.id)
            .values(
                flaky_score=test_case.flaky_score,
                flaky_since=test_case.flaky_since,
                disagreed_at=test_case.disagreed_at,
                quarantined_at=test_case.quarantined_at,
                quarantined_by=test_case.quarantined_by,
                quarantine_reason=test_case.quarantine_reason,
            )
        )

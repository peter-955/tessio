from uuid import UUID

from sqlalchemy import select

from app.modules.test_cases.domains.test_case_version.entity import TestCaseVersion
from app.modules.test_cases.domains.test_case_version.repository import TestCaseVersionRepository
from app.modules.test_cases.infrastructure.test_case_version_table import TestCaseVersionTable
from app.shared.postgres import Database


class PostgresTestCaseVersionRepository(TestCaseVersionRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_id(self, version_id: UUID) -> TestCaseVersion | None:
        row = await self._database.get_current_session().scalar(
            select(TestCaseVersionTable)
            .where(TestCaseVersionTable.id == version_id)
            .execution_options(populate_existing=True)
        )
        return None if row is None else TestCaseVersion.model_validate(row)

    async def list_for_case(self, test_case_id: UUID) -> list[TestCaseVersion]:
        rows = await self._database.get_current_session().scalars(
            select(TestCaseVersionTable)
            .where(TestCaseVersionTable.test_case_id == test_case_id)
            .order_by(TestCaseVersionTable.number.desc())
            .execution_options(populate_existing=True)
        )
        return [TestCaseVersion.model_validate(row) for row in rows]

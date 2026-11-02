from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError

from app.modules.suites.domains.test_suite.entity import TestSuite
from app.modules.suites.domains.test_suite.repository import TestSuiteRepository
from app.modules.suites.errors import SuiteNameAlreadyUsedError
from app.modules.suites.infrastructure.test_suite_table import TestSuiteTable
from app.modules.suites.typing.constants.suite import ACTIVE_SUITE_NAME_INDEX
from app.shared.postgres import Database, read_constraint_name


class PostgresTestSuiteRepository(TestSuiteRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_id(self, project_id: UUID, suite_id: UUID) -> TestSuite | None:
        row = await self._database.get_current_session().scalar(
            select(TestSuiteTable)
            .where(TestSuiteTable.project_id == project_id, TestSuiteTable.id == suite_id)
            .execution_options(populate_existing=True)
        )
        return None if row is None else TestSuite.model_validate(row)

    async def find_by_id_for_update(self, project_id: UUID, suite_id: UUID) -> TestSuite | None:
        row = await self._database.get_current_session().scalar(
            select(TestSuiteTable)
            .where(TestSuiteTable.project_id == project_id, TestSuiteTable.id == suite_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else TestSuite.model_validate(row)

    async def find_active_by_name(self, project_id: UUID, name: str) -> TestSuite | None:
        row = await self._database.get_current_session().scalar(
            select(TestSuiteTable).where(
                TestSuiteTable.project_id == project_id,
                TestSuiteTable.archived_at.is_(None),
                func.lower(TestSuiteTable.name) == name.strip().lower(),
            )
        )
        return None if row is None else TestSuite.model_validate(row)

    async def add(self, suite: TestSuite) -> None:
        session = self._database.get_current_session()
        session.add(TestSuiteTable(**suite.model_dump()))
        await self._flush()

    async def save(self, suite: TestSuite) -> None:
        await self._database.get_current_session().merge(TestSuiteTable(**suite.model_dump()))
        await self._flush()

    async def _flush(self) -> None:
        try:
            await self._database.get_current_session().flush()
        except IntegrityError as error:
            if read_constraint_name(error) == ACTIVE_SUITE_NAME_INDEX:
                raise SuiteNameAlreadyUsedError from error
            raise

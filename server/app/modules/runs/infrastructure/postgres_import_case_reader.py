from collections.abc import Collection
from uuid import UUID

from sqlalchemy import select

from app.modules.runs.domains.import_case.entity import ImportCase
from app.modules.runs.ports.import_case_reader import ImportCaseReader
from app.modules.test_cases import TestCaseStatus, TestCaseVersion
from app.modules.test_cases.infrastructure import TestCaseTable, TestCaseVersionTable
from app.shared.postgres import Database


class PostgresImportCaseReader(ImportCaseReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_by_numbers(self, project_id: UUID, numbers: Collection[int]) -> list[ImportCase]:
        if not numbers:
            return []
        result = await self._database.get_current_session().execute(
            select(TestCaseTable.id, TestCaseTable.number, TestCaseTable.story_id, TestCaseVersionTable)
            .join(TestCaseVersionTable, TestCaseVersionTable.id == TestCaseTable.current_version_id)
            .where(
                TestCaseTable.project_id == project_id,
                TestCaseTable.number.in_(sorted(numbers)),
                TestCaseTable.status != TestCaseStatus.DEPRECATED,
            )
            .order_by(TestCaseTable.number)
            .execution_options(populate_existing=True)
        )
        return [
            ImportCase(
                test_case_id=test_case_id,
                number=number,
                story_id=story_id,
                version=TestCaseVersion.model_validate(version_row),
            )
            for test_case_id, number, story_id, version_row in result
        ]

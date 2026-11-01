from uuid import UUID

from sqlalchemy import func, insert, select, update

from app.modules.files.infrastructure import StoredFileTable
from app.modules.test_cases.domains.test_file.entity import TestFile
from app.modules.test_cases.domains.test_file.repository import TestFileRepository
from app.modules.test_cases.domains.test_file_detail.entity import TestFileDetail
from app.modules.test_cases.domains.test_file_version.entity import TestFileVersion
from app.modules.test_cases.domains.test_file_version_detail.entity import TestFileVersionDetail
from app.modules.test_cases.infrastructure.test_file_table import TestFileTable
from app.modules.test_cases.infrastructure.test_file_version_table import TestFileVersionTable
from app.shared.postgres import Database


class PostgresTestFileRepository(TestFileRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_for_case(self, test_case_id: UUID) -> list[TestFileDetail]:
        version_count = (
            select(func.count(TestFileVersionTable.id))
            .where(TestFileVersionTable.test_file_id == TestFileTable.id)
            .correlate(TestFileTable)
            .scalar_subquery()
        )
        result = await self._database.get_current_session().execute(
            select(
                TestFileTable,
                TestFileVersionTable,
                StoredFileTable.file_name,
                StoredFileTable.content_type,
                StoredFileTable.size,
                version_count,
            )
            .join(TestFileVersionTable, TestFileVersionTable.id == TestFileTable.current_version_id)
            .join(StoredFileTable, StoredFileTable.id == TestFileVersionTable.stored_file_id)
            .where(TestFileTable.test_case_id == test_case_id)
            .order_by(TestFileTable.key)
            .execution_options(populate_existing=True)
        )
        return [
            TestFileDetail(
                test_file=TestFile.model_validate(file_row),
                current_version=TestFileVersionDetail(
                    version=TestFileVersion.model_validate(version_row),
                    file_name=file_name,
                    content_type=content_type,
                    size=size,
                ),
                version_count=count,
            )
            for file_row, version_row, file_name, content_type, size, count in result
        ]

    async def find_by_key(self, test_case_id: UUID, key: str) -> TestFile | None:
        row = await self._database.get_current_session().scalar(
            select(TestFileTable)
            .where(TestFileTable.test_case_id == test_case_id, TestFileTable.key == key)
            .execution_options(populate_existing=True)
        )
        return None if row is None else TestFile.model_validate(row)

    async def create(self, test_file: TestFile, version: TestFileVersion) -> None:
        session = self._database.get_current_session()
        await session.execute(insert(TestFileTable).values({**test_file.model_dump(), "current_version_id": None}))
        await self.add_version(test_file, version)

    async def add_version(self, test_file: TestFile, version: TestFileVersion) -> None:
        session = self._database.get_current_session()
        await session.execute(insert(TestFileVersionTable).values(**version.model_dump()))
        await session.execute(
            update(TestFileTable).where(TestFileTable.id == test_file.id).values(current_version_id=version.id)
        )

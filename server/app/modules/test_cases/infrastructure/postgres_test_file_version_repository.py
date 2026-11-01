from uuid import UUID

from sqlalchemy import exists, select

from app.modules.files.infrastructure import StoredFileTable
from app.modules.test_cases.domains.test_file_version.entity import TestFileVersion
from app.modules.test_cases.domains.test_file_version.repository import TestFileVersionRepository
from app.modules.test_cases.domains.test_file_version_detail.entity import TestFileVersionDetail
from app.modules.test_cases.infrastructure.test_file_version_table import TestFileVersionTable
from app.shared.postgres import Database


class PostgresTestFileVersionRepository(TestFileVersionRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_for_file(self, test_file_id: UUID) -> list[TestFileVersionDetail]:
        result = await self._database.get_current_session().execute(
            select(TestFileVersionTable, StoredFileTable.file_name, StoredFileTable.content_type, StoredFileTable.size)
            .join(StoredFileTable, StoredFileTable.id == TestFileVersionTable.stored_file_id)
            .where(TestFileVersionTable.test_file_id == test_file_id)
            .order_by(TestFileVersionTable.number.desc())
            .execution_options(populate_existing=True)
        )
        return [
            TestFileVersionDetail(
                version=TestFileVersion.model_validate(row), file_name=file_name, content_type=content_type, size=size
            )
            for row, file_name, content_type, size in result
        ]

    async def exists_for_stored_file(self, stored_file_id: UUID) -> bool:
        is_attached = await self._database.get_current_session().scalar(
            select(exists().where(TestFileVersionTable.stored_file_id == stored_file_id))
        )
        return bool(is_attached)

from uuid import UUID

from sqlalchemy import any_, func, select

from app.modules.files import StoredFileStatus
from app.modules.files.infrastructure import StoredFileTable
from app.modules.runs.infrastructure import RunCaseTable, RunTable
from app.modules.runs.typing.enums import RunStatus
from app.modules.story_context.domains.run_scope.entity import RunScope
from app.modules.story_context.domains.run_test_file.entity import RunTestFile
from app.modules.story_context.ports.run_scope_reader import RunScopeReader
from app.modules.test_cases.infrastructure import TestCaseVersionTable, TestFileTable, TestFileVersionTable
from app.shared.postgres import Database


class PostgresRunScopeReader(RunScopeReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_run(self, project_id: UUID, run_id: UUID) -> RunScope | None:
        result = await self._database.get_current_session().execute(
            select(
                RunTable.id, RunTable.project_id, RunTable.environment_id, RunTable.started_by, RunTable.status
            ).where(RunTable.id == run_id, RunTable.project_id == project_id)
        )
        row = result.one_or_none()
        if row is None:
            return None
        found_run_id, found_project_id, environment_id, started_by, status = row
        return RunScope(
            id=found_run_id,
            project_id=found_project_id,
            environment_id=environment_id,
            started_by=started_by,
            is_running=status == RunStatus.RUNNING,
        )

    async def list_data_keys(self, run_id: UUID) -> frozenset[str]:
        data_key = func.unnest(TestCaseVersionTable.data_keys).label("data_key")
        result = await self._database.get_current_session().scalars(
            select(data_key)
            .select_from(RunCaseTable)
            .join(TestCaseVersionTable, TestCaseVersionTable.id == RunCaseTable.test_case_version_id)
            .where(RunCaseTable.run_id == run_id)
            .distinct()
        )
        return frozenset(result)

    async def list_test_files(self, run_id: UUID, key: str, test_case_id: UUID | None) -> list[RunTestFile]:
        statement = (
            select(
                RunCaseTable.test_case_id,
                TestFileVersionTable.id,
                TestFileTable.key,
                StoredFileTable.file_name,
                StoredFileTable.object_key,
                StoredFileTable.status,
            )
            .select_from(RunCaseTable)
            .join(TestCaseVersionTable, TestCaseVersionTable.id == RunCaseTable.test_case_version_id)
            .join(TestFileVersionTable, TestFileVersionTable.id == any_(TestCaseVersionTable.file_version_ids))
            .join(
                TestFileTable,
                (TestFileTable.id == TestFileVersionTable.test_file_id)
                & (TestFileTable.test_case_id == RunCaseTable.test_case_id),
            )
            .join(StoredFileTable, StoredFileTable.id == TestFileVersionTable.stored_file_id)
            .where(RunCaseTable.run_id == run_id, TestFileTable.key == key)
            .order_by(RunCaseTable.position)
        )
        if test_case_id is not None:
            statement = statement.where(RunCaseTable.test_case_id == test_case_id)
        result = await self._database.get_current_session().execute(statement)
        return [
            RunTestFile(
                test_case_id=found_test_case_id,
                test_file_version_id=test_file_version_id,
                key=file_key,
                file_name=file_name,
                object_key=object_key,
                is_uploaded=status == StoredFileStatus.UPLOADED,
            )
            for found_test_case_id, test_file_version_id, file_key, file_name, object_key, status in result
        ]

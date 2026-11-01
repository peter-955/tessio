from sqlalchemy.dialects.postgresql import insert

from app.modules.runs.infrastructure import RunFileTable
from app.modules.story_context.domains.run_file.entity import RunFile
from app.modules.story_context.ports.run_file_recorder import RunFileRecorder
from app.shared.postgres import Database


class PostgresRunFileRecorder(RunFileRecorder):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def record(self, run_file: RunFile) -> None:
        await self._database.get_current_session().execute(
            insert(RunFileTable)
            .values(
                id=run_file.id,
                run_id=run_file.run_id,
                test_case_id=run_file.test_case_id,
                test_file_version_id=run_file.test_file_version_id,
                key=run_file.key,
                requested_by=run_file.requested_by,
                created_at=run_file.created_at,
            )
            .on_conflict_do_nothing(index_elements=["run_id", "test_case_id", "key"])
        )

from uuid import UUID

from sqlalchemy import delete, select

from app.modules.run_logs.domains.run_log.entity import RunLog
from app.modules.run_logs.domains.run_log.repository import RunLogRepository
from app.modules.run_logs.domains.run_log_entry.entity import RunLogEntry
from app.modules.run_logs.infrastructure.run_log_entry_table import RunLogEntryTable
from app.modules.run_logs.infrastructure.run_log_table import RunLogTable
from app.shared.postgres import Database


class PostgresRunLogRepository(RunLogRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def replace(self, run_log: RunLog, entries: list[RunLogEntry]) -> None:
        session = self._database.get_current_session()
        await session.execute(delete(RunLogEntryTable).where(RunLogEntryTable.run_id == run_log.run_id))
        await session.merge(RunLogTable(**run_log.model_dump()))
        session.add_all(RunLogEntryTable(**entry.model_dump()) for entry in entries)
        await session.flush()

    async def find(self, run_id: UUID) -> RunLog | None:
        row = await self._database.get_current_session().scalar(select(RunLogTable).where(RunLogTable.run_id == run_id))
        return None if row is None else RunLog.model_validate(row)

    async def list_entries(self, run_id: UUID, test_case_id: UUID | None) -> list[RunLogEntry]:
        statement = select(RunLogEntryTable).where(RunLogEntryTable.run_id == run_id)
        if test_case_id is not None:
            statement = statement.where(RunLogEntryTable.test_case_id == test_case_id)
        rows = await self._database.get_current_session().scalars(statement.order_by(RunLogEntryTable.position))
        return [RunLogEntry.model_validate(row) for row in rows]

from uuid import UUID

from sqlalchemy import exists, select

from app.modules.runs.infrastructure.run_table import RunTable
from app.modules.runs.typing.enums import RunStatus
from app.modules.stories import RunningRunChecker
from app.shared.postgres import Database


class PostgresRunningRunChecker(RunningRunChecker):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def has_running_run(self, project_id: UUID, story_id: UUID) -> bool:
        async with self._database.begin():
            is_running = await self._database.get_current_session().scalar(
                select(
                    exists().where(
                        RunTable.project_id == project_id,
                        RunTable.story_id == story_id,
                        RunTable.status == RunStatus.RUNNING,
                    )
                )
            )
        return bool(is_running)

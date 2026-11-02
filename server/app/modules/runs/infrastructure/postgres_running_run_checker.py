from uuid import UUID

from sqlalchemy import exists, or_, select

from app.modules.runs.infrastructure.run_case_table import RunCaseTable
from app.modules.runs.infrastructure.run_table import RunTable
from app.modules.runs.typing.enums import RunStatus
from app.modules.stories import RunningRunChecker
from app.modules.test_cases.infrastructure import TestCaseTable
from app.shared.postgres import Database


class PostgresRunningRunChecker(RunningRunChecker):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def has_running_run(self, project_id: UUID, story_id: UUID) -> bool:
        holds_case_of_story = (
            exists()
            .where(
                RunCaseTable.run_id == RunTable.id,
                TestCaseTable.id == RunCaseTable.test_case_id,
                TestCaseTable.story_id == story_id,
            )
            .correlate(RunTable)
        )
        async with self._database.begin():
            is_running = await self._database.get_current_session().scalar(
                select(
                    exists().where(
                        RunTable.project_id == project_id,
                        RunTable.status == RunStatus.RUNNING,
                        or_(
                            RunTable.story_id == story_id,
                            RunTable.test_suite_id.is_not(None) & holds_case_of_story,
                        ),
                    )
                )
            )
        return bool(is_running)

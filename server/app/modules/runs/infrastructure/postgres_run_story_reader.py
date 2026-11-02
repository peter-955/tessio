from uuid import UUID

from sqlalchemy import select

from app.modules.runs.infrastructure.suite_name_table import SUITE_NAME_TABLE
from app.modules.runs.ports.run_story_reader import RunStoryReader
from app.modules.stories.infrastructure import StoryTable
from app.shared.postgres import Database


class PostgresRunStoryReader(RunStoryReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_jira_key(self, story_id: UUID) -> str:
        jira_key: str = (
            await self._database.get_current_session().execute(
                select(StoryTable.jira_key).where(StoryTable.id == story_id)
            )
        ).scalar_one()
        return jira_key

    async def find_suite_name(self, suite_id: UUID) -> str:
        suite_name: str = (
            await self._database.get_current_session().execute(
                select(SUITE_NAME_TABLE.c.name).where(SUITE_NAME_TABLE.c.id == suite_id)
            )
        ).scalar_one()
        return suite_name

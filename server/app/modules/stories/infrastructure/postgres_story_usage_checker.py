from uuid import UUID

from sqlalchemy import Uuid, column, exists, or_, select, table

from app.modules.stories.ports.story_usage_checker import StoryUsageChecker
from app.shared.postgres import Database

STORY_REFERENCES = tuple(table(name, column("story_id", Uuid())) for name in ("test_cases", "runs", "gaps"))


class PostgresStoryUsageChecker(StoryUsageChecker):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def is_in_use(self, story_id: UUID) -> bool:
        is_used = await self._database.get_current_session().scalar(
            select(or_(*(exists().where(reference.c.story_id == story_id) for reference in STORY_REFERENCES)))
        )
        return bool(is_used)

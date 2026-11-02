from datetime import datetime
from uuid import UUID

from sqlalchemy.dialects.postgresql import insert

from app.modules.stories.domains.story_key_counter.repository import StoryKeyCounterRepository
from app.modules.stories.infrastructure.story_key_counter_table import StoryKeyCounterTable
from app.shared.postgres import Database


class PostgresStoryKeyCounterRepository(StoryKeyCounterRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def allocate_number(self, project_id: UUID, now: datetime) -> int:
        number = await self._database.get_current_session().scalar(
            insert(StoryKeyCounterTable)
            .values(project_id=project_id, last_number=1, created_at=now)
            .on_conflict_do_update(
                index_elements=["project_id"], set_={"last_number": StoryKeyCounterTable.last_number + 1}
            )
            .returning(StoryKeyCounterTable.last_number)
        )
        if not isinstance(number, int):
            raise RuntimeError("Story key counter upsert returned no number")
        return number

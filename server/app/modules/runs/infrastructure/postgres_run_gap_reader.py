from collections.abc import Collection
from uuid import UUID

from sqlalchemy import select

from app.modules.gaps.infrastructure import GapTable
from app.modules.gaps.typing.enums import GapStatus
from app.modules.runs.domains.blocking_gap.entity import BlockingGap
from app.modules.runs.ports.run_gap_reader import RunGapReader
from app.modules.stories.infrastructure import StoryTable
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresRunGapReader(RunGapReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_open_gaps(self, project_id: UUID, story_ids: Collection[UUID]) -> list[BlockingGap]:
        if not story_ids:
            return []
        result = await self._database.get_current_session().execute(
            select(GapTable.id, StoryTable.jira_key, GapTable.question, UserTable.name, GapTable.assignee_role)
            .join(StoryTable, StoryTable.id == GapTable.story_id)
            .outerjoin(UserTable, UserTable.id == GapTable.assignee_id)
            .where(
                GapTable.project_id == project_id,
                GapTable.story_id.in_(story_ids),
                GapTable.status == GapStatus.OPEN,
            )
            .order_by(StoryTable.jira_key, GapTable.created_at, GapTable.id)
        )
        return [
            BlockingGap(
                gap_id=gap_id,
                story_jira_key=jira_key,
                question=question,
                assignee_name=assignee_name,
                assignee_role=assignee_role,
            )
            for gap_id, jira_key, question, assignee_name, assignee_role in result
        ]

from uuid import UUID

from sqlalchemy import Select, func, select

from app.modules.insights.domains.sprint_reference.entity import SprintReference
from app.modules.insights.domains.traced_story.entity import TracedStory
from app.modules.insights.ports.story_scope_reader import StoryScopeReader
from app.modules.stories import SprintState, TestStatus
from app.modules.stories.infrastructure import SprintTable, StoryTable
from app.shared.postgres import Database


class PostgresStoryScopeReader(StoryScopeReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_story(self, project_id: UUID, jira_key: str) -> TracedStory | None:
        result = await self._database.get_current_session().execute(
            self._select_stories().where(
                StoryTable.project_id == project_id, StoryTable.jira_key == jira_key.strip().upper()
            )
        )
        row = result.one_or_none()
        if row is None:
            return None
        story_id, story_jira_key, title, test_status = row
        return TracedStory(id=story_id, jira_key=story_jira_key, title=title, test_status=test_status)

    async def list_stories(
        self, project_id: UUID, sprint_id: UUID | None, is_excluding_missing: bool
    ) -> list[TracedStory]:
        statement = (
            self._select_stories()
            .where(StoryTable.project_id == project_id)
            .order_by(func.length(StoryTable.jira_key), StoryTable.jira_key)
        )
        if sprint_id is not None:
            statement = statement.where(StoryTable.sprint_id == sprint_id)
        if is_excluding_missing:
            statement = statement.where(StoryTable.jira_missing_at.is_(None))
        result = await self._database.get_current_session().execute(statement)
        return [
            TracedStory(id=story_id, jira_key=story_jira_key, title=title, test_status=test_status)
            for story_id, story_jira_key, title, test_status in result
        ]

    async def find_sprint(self, project_id: UUID, sprint_id: UUID) -> SprintReference | None:
        row = await self._database.get_current_session().scalar(
            select(SprintTable).where(SprintTable.project_id == project_id, SprintTable.id == sprint_id)
        )
        return None if row is None else self._build_sprint(row)

    async def find_current_sprint(self, project_id: UUID) -> SprintReference | None:
        row = await self._database.get_current_session().scalar(
            select(SprintTable)
            .where(SprintTable.project_id == project_id, SprintTable.state == SprintState.ACTIVE)
            .order_by(SprintTable.start_at.desc().nulls_last(), SprintTable.jira_sprint_id.desc())
            .limit(1)
        )
        return None if row is None else self._build_sprint(row)

    @staticmethod
    def _select_stories() -> Select[UUID, str, str, TestStatus]:
        return select(StoryTable.id, StoryTable.jira_key, StoryTable.title, StoryTable.test_status)

    @staticmethod
    def _build_sprint(row: SprintTable) -> SprintReference:
        return SprintReference(id=row.id, name=row.name, state=row.state, start_at=row.start_at, end_at=row.end_at)

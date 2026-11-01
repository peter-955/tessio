from uuid import UUID

from sqlalchemy import ColumnElement, select

from app.modules.stories.infrastructure import StoryTable
from app.modules.test_cases.domains.case_story.entity import CaseStory
from app.modules.test_cases.ports.story_reader import StoryReader
from app.shared.postgres import Database


class PostgresStoryReader(StoryReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_jira_key(self, project_id: UUID, jira_key: str) -> CaseStory | None:
        stories = await self._list(project_id, StoryTable.jira_key == jira_key)
        return stories[0] if stories else None

    async def find_by_id(self, project_id: UUID, story_id: UUID) -> CaseStory | None:
        stories = await self._list(project_id, StoryTable.id == story_id)
        return stories[0] if stories else None

    async def list_by_jira_keys(self, project_id: UUID, jira_keys: frozenset[str]) -> list[CaseStory]:
        return await self._list(project_id, StoryTable.jira_key.in_(sorted(jira_keys)))

    async def _list(self, project_id: UUID, *conditions: ColumnElement[bool]) -> list[CaseStory]:
        result = await self._database.get_current_session().execute(
            select(StoryTable.id, StoryTable.jira_key, StoryTable.title)
            .where(StoryTable.project_id == project_id, *conditions)
            .order_by(StoryTable.jira_key)
        )
        return [CaseStory(id=story_id, jira_key=jira_key, title=title) for story_id, jira_key, title in result]

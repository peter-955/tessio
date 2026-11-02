from datetime import datetime
from uuid import UUID

from sqlalchemy import delete, func, or_, select, update
from sqlalchemy.dialects.postgresql import insert

from app.modules.stories.domains.story.entity import Story
from app.modules.stories.domains.story.repository import StoryRepository
from app.modules.stories.domains.story_filter.entity import StoryFilter
from app.modules.stories.domains.story_summary.entity import StorySummary
from app.modules.stories.infrastructure.acceptance_criterion_table import AcceptanceCriterionTable
from app.modules.stories.infrastructure.sprint_table import SprintTable
from app.modules.stories.infrastructure.story_table import StoryTable
from app.modules.stories.typing.constants import LIKE_ESCAPE_CHARACTER
from app.modules.stories.typing.enums import TestStatus
from app.modules.stories.utils.like_pattern import build_contains_pattern
from app.shared.postgres import Database


class PostgresStoryRepository(StoryRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_by_jira_key(self, project_id: UUID, jira_key: str) -> Story | None:
        row = await self._database.get_current_session().scalar(
            select(StoryTable).where(StoryTable.project_id == project_id, StoryTable.jira_key == jira_key)
        )
        return None if row is None else Story.model_validate(row)

    async def find_by_jira_key_for_update(self, project_id: UUID, jira_key: str) -> Story | None:
        row = await self._database.get_current_session().scalar(
            select(StoryTable)
            .where(StoryTable.project_id == project_id, StoryTable.jira_key == jira_key)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else Story.model_validate(row)

    async def find_by_id_for_update(self, project_id: UUID, story_id: UUID) -> Story | None:
        row = await self._database.get_current_session().scalar(
            select(StoryTable)
            .where(StoryTable.project_id == project_id, StoryTable.id == story_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        return None if row is None else Story.model_validate(row)

    async def list_summaries(self, project_id: UUID, story_filter: StoryFilter) -> list[StorySummary]:
        criterion_count = (
            select(func.count(AcceptanceCriterionTable.id))
            .where(AcceptanceCriterionTable.story_id == StoryTable.id, AcceptanceCriterionTable.removed_at.is_(None))
            .correlate(StoryTable)
            .scalar_subquery()
        )
        statement = (
            select(StoryTable, SprintTable.name, criterion_count)
            .outerjoin(SprintTable, SprintTable.id == StoryTable.sprint_id)
            .where(StoryTable.project_id == project_id)
            .order_by(func.length(StoryTable.jira_key), StoryTable.jira_key)
        )
        if story_filter.sprint_id is not None:
            statement = statement.where(StoryTable.sprint_id == story_filter.sprint_id)
        if story_filter.test_status is not None:
            statement = statement.where(StoryTable.test_status == story_filter.test_status)
        if story_filter.query is not None:
            pattern = build_contains_pattern(story_filter.query)
            statement = statement.where(
                or_(
                    StoryTable.jira_key.ilike(pattern, escape=LIKE_ESCAPE_CHARACTER),
                    StoryTable.title.ilike(pattern, escape=LIKE_ESCAPE_CHARACTER),
                )
            )
        result = await self._database.get_current_session().execute(statement)
        return [
            StorySummary(story=Story.model_validate(row), sprint_name=sprint_name, criterion_count=count)
            for row, sprint_name, count in result
        ]

    async def save_synced(self, story: Story) -> UUID:
        statement = insert(StoryTable).values(**story.model_dump())
        story_id = await self._database.get_current_session().scalar(
            statement.on_conflict_do_update(
                index_elements=[StoryTable.project_id, StoryTable.jira_id],
                set_={
                    "sprint_id": statement.excluded.sprint_id,
                    "jira_key": statement.excluded.jira_key,
                    "jira_url": statement.excluded.jira_url,
                    "title": statement.excluded.title,
                    "description": statement.excluded.description,
                    "jira_status": statement.excluded.jira_status,
                    "jira_issue_type": statement.excluded.jira_issue_type,
                    "jira_updated_at": statement.excluded.jira_updated_at,
                    "synced_at": statement.excluded.synced_at,
                    "jira_missing_at": None,
                    "updated_at": func.now(),
                },
            ).returning(StoryTable.id)
        )
        if not isinstance(story_id, UUID):
            raise RuntimeError("Story upsert returned no id")
        return story_id

    async def save(self, story: Story) -> None:
        await self._database.get_current_session().merge(StoryTable(**story.model_dump()))

    async def delete(self, story_id: UUID) -> None:
        await self._database.get_current_session().execute(delete(StoryTable).where(StoryTable.id == story_id))

    async def update_test_status(
        self, story_id: UUID, test_status: TestStatus, changed_by: UUID, changed_at: datetime
    ) -> None:
        await self._database.get_current_session().execute(
            update(StoryTable)
            .where(StoryTable.id == story_id)
            .values(test_status=test_status, test_status_changed_at=changed_at, test_status_changed_by=changed_by)
        )

    async def mark_missing(
        self, project_id: UUID, seen_jira_ids: frozenset[str], sprint_ids: frozenset[UUID], now: datetime
    ) -> int:
        updated_ids = await self._database.get_current_session().scalars(
            update(StoryTable)
            .where(
                StoryTable.project_id == project_id,
                StoryTable.jira_missing_at.is_(None),
                StoryTable.jira_id.not_in(sorted(seen_jira_ids)),
                or_(StoryTable.sprint_id.in_(sorted(sprint_ids)), StoryTable.sprint_id.is_(None)),
            )
            .values(jira_missing_at=now)
            .returning(StoryTable.id)
        )
        return len(updated_ids.all())

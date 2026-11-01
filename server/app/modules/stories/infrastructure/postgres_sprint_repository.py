from uuid import UUID

from sqlalchemy import Select, case, func, select
from sqlalchemy.dialects.postgresql import insert

from app.modules.stories.domains.sprint.entity import Sprint
from app.modules.stories.domains.sprint.repository import SprintRepository
from app.modules.stories.domains.sprint_overview.entity import SprintOverview
from app.modules.stories.infrastructure.sprint_table import SprintTable
from app.modules.stories.infrastructure.story_table import StoryTable
from app.modules.stories.typing.enums import SprintState
from app.shared.postgres import Database


class PostgresSprintRepository(SprintRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find_overview(self, project_id: UUID, sprint_id: UUID) -> SprintOverview | None:
        result = await self._database.get_current_session().execute(
            self._select_overviews().where(SprintTable.project_id == project_id, SprintTable.id == sprint_id)
        )
        found = result.first()
        if found is None:
            return None
        row, story_count = found
        return SprintOverview(sprint=Sprint.model_validate(row), story_count=story_count)

    async def find_by_id(self, project_id: UUID, sprint_id: UUID) -> Sprint | None:
        row = await self._database.get_current_session().scalar(
            select(SprintTable).where(SprintTable.project_id == project_id, SprintTable.id == sprint_id)
        )
        return None if row is None else Sprint.model_validate(row)

    async def list_by_project(self, project_id: UUID) -> list[Sprint]:
        rows = await self._database.get_current_session().scalars(
            select(SprintTable).where(SprintTable.project_id == project_id).order_by(SprintTable.jira_sprint_id)
        )
        return [Sprint.model_validate(row) for row in rows]

    async def save_synced(self, sprint: Sprint) -> UUID:
        statement = insert(SprintTable).values(**sprint.model_dump())
        sprint_id = await self._database.get_current_session().scalar(
            statement.on_conflict_do_update(
                index_elements=[SprintTable.project_id, SprintTable.jira_sprint_id],
                set_={
                    "name": statement.excluded.name,
                    "state": statement.excluded.state,
                    "start_at": statement.excluded.start_at,
                    "end_at": statement.excluded.end_at,
                    "complete_at": statement.excluded.complete_at,
                    "synced_at": statement.excluded.synced_at,
                    "updated_at": func.now(),
                },
            ).returning(SprintTable.id)
        )
        if not isinstance(sprint_id, UUID):
            raise RuntimeError("Sprint upsert returned no id")
        return sprint_id

    async def list(self, project_id: UUID) -> list[SprintOverview]:
        state_rank = case(
            (SprintTable.state == SprintState.ACTIVE, 0), (SprintTable.state == SprintState.FUTURE, 1), else_=2
        )
        future_start_at = case((SprintTable.state == SprintState.FUTURE, SprintTable.start_at))
        closed_complete_at = case((SprintTable.state == SprintState.CLOSED, SprintTable.complete_at))
        statement = (
            self._select_overviews()
            .where(SprintTable.project_id == project_id)
            .order_by(
                state_rank,
                future_start_at.asc().nulls_last(),
                closed_complete_at.desc().nulls_last(),
                SprintTable.start_at.asc().nulls_last(),
                SprintTable.jira_sprint_id,
            )
        )
        result = await self._database.get_current_session().execute(statement)
        return [
            SprintOverview(sprint=Sprint.model_validate(row), story_count=story_count) for row, story_count in result
        ]

    @staticmethod
    def _select_overviews() -> Select[SprintTable, int]:
        story_count = (
            select(func.count(StoryTable.id))
            .where(StoryTable.sprint_id == SprintTable.id, StoryTable.jira_missing_at.is_(None))
            .correlate(SprintTable)
            .scalar_subquery()
        )
        return select(SprintTable, story_count)

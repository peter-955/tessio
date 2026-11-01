from datetime import datetime
from uuid import UUID

from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from app.modules.stories.domains.project_sync_state.entity import ProjectSyncState
from app.modules.stories.domains.project_sync_state.repository import ProjectSyncStateRepository
from app.modules.stories.infrastructure.project_sync_state_table import ProjectSyncStateTable
from app.modules.stories.typing.enums import ProjectSyncStatus
from app.shared.postgres import Database


class PostgresProjectSyncStateRepository(ProjectSyncStateRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find(self, project_id: UUID) -> ProjectSyncState | None:
        row = await self._database.get_current_session().get(ProjectSyncStateTable, project_id)
        return None if row is None else ProjectSyncState.model_validate(row)

    async def lock(self, project_id: UUID, now: datetime) -> ProjectSyncState:
        session = self._database.get_current_session()
        await session.execute(
            insert(ProjectSyncStateTable)
            .values(project_id=project_id, status=ProjectSyncStatus.NEVER, created_at=now)
            .on_conflict_do_nothing(index_elements=[ProjectSyncStateTable.project_id])
        )
        row = await session.scalar(
            select(ProjectSyncStateTable)
            .where(ProjectSyncStateTable.project_id == project_id)
            .with_for_update()
            .execution_options(populate_existing=True)
        )
        if row is None:
            raise RuntimeError("Project sync state row missing after insert")
        return ProjectSyncState.model_validate(row)

    async def save(self, state: ProjectSyncState) -> None:
        await self._database.get_current_session().execute(
            update(ProjectSyncStateTable)
            .where(ProjectSyncStateTable.project_id == state.project_id)
            .values(
                status=state.status,
                requested_by=state.requested_by,
                queued_at=state.queued_at,
                started_at=state.started_at,
                finished_at=state.finished_at,
                last_succeeded_at=state.last_succeeded_at,
                error_code=None if state.error_code is None else state.error_code.value,
            )
        )

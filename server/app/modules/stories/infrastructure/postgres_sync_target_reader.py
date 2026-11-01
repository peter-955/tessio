from uuid import UUID

from sqlalchemy import select

from app.modules.projects.infrastructure import ProjectTable
from app.modules.stories.domains.sync_target.entity import SyncTarget
from app.modules.stories.ports.sync_target_reader import SyncTargetReader
from app.shared.postgres import Database


class PostgresSyncTargetReader(SyncTargetReader):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find(self, project_id: UUID) -> SyncTarget | None:
        result = await self._database.get_current_session().execute(
            select(
                ProjectTable.id,
                ProjectTable.key,
                ProjectTable.jira_project_key,
                ProjectTable.jira_board_id,
                ProjectTable.archived_at,
            ).where(ProjectTable.id == project_id)
        )
        found = result.first()
        if found is None:
            return None
        found_id, key, jira_project_key, jira_board_id, archived_at = found
        return SyncTarget(
            project_id=found_id,
            project_key=key,
            jira_project_key=jira_project_key,
            jira_board_id=jira_board_id,
            is_archived=archived_at is not None,
        )

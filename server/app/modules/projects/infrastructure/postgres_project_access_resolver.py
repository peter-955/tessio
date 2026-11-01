from uuid import UUID

from sqlalchemy import ColumnElement, and_, select

from app.modules.projects.infrastructure.project_member_table import ProjectMemberTable
from app.modules.projects.infrastructure.project_table import ProjectTable
from app.modules.projects.utils.effective_role import is_acting_as_workspace_admin, resolve_effective_role
from app.shared.permissions import Actor, ProjectAccess, ProjectAccessResolver, ProjectNotFoundError
from app.shared.postgres import Database


class PostgresProjectAccessResolver(ProjectAccessResolver):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def resolve(self, actor: Actor, project_key: str) -> ProjectAccess:
        return await self._resolve_where(actor, ProjectTable.key == project_key)

    async def resolve_by_id(self, actor: Actor, project_id: UUID) -> ProjectAccess:
        return await self._resolve_where(actor, ProjectTable.id == project_id)

    async def list_visible_project_ids(self, actor: Actor) -> frozenset[UUID]:
        if is_acting_as_workspace_admin(actor):
            statement = select(ProjectTable.id)
        else:
            statement = select(ProjectMemberTable.project_id).where(ProjectMemberTable.user_id == actor.user_id)
        project_ids = frozenset(await self._database.get_current_session().scalars(statement))
        if actor.token_project_id is not None:
            return project_ids & {actor.token_project_id}
        return project_ids

    async def _resolve_where(self, actor: Actor, condition: ColumnElement[bool]) -> ProjectAccess:
        result = await self._database.get_current_session().execute(
            select(ProjectTable.id, ProjectTable.key, ProjectTable.archived_at, ProjectMemberTable.role)
            .outerjoin(
                ProjectMemberTable,
                and_(ProjectMemberTable.project_id == ProjectTable.id, ProjectMemberTable.user_id == actor.user_id),
            )
            .where(condition)
        )
        row = result.one_or_none()
        if row is None:
            raise ProjectNotFoundError
        project_id, project_key, archived_at, member_role = row
        if actor.token_project_id is not None and actor.token_project_id != project_id:
            raise ProjectNotFoundError
        return ProjectAccess(
            project_id=project_id,
            project_key=project_key,
            role=resolve_effective_role(actor, member_role),
            is_archived=archived_at is not None,
        )

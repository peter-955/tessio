from uuid import UUID

from sqlalchemy import delete, func, select

from app.modules.projects.domains.project_member.entity import ProjectMember
from app.modules.projects.domains.project_member.repository import ProjectMemberRepository
from app.modules.projects.infrastructure.project_member_table import ProjectMemberTable
from app.shared.permissions import ProjectRole
from app.shared.postgres import Database


class PostgresProjectMemberRepository(ProjectMemberRepository):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def find(self, project_id: UUID, user_id: UUID) -> ProjectMember | None:
        row = await self._database.get_current_session().scalar(
            select(ProjectMemberTable).where(
                ProjectMemberTable.project_id == project_id, ProjectMemberTable.user_id == user_id
            )
        )
        return None if row is None else ProjectMember.model_validate(row)

    async def list_for_user(self, user_id: UUID) -> list[ProjectMember]:
        rows = await self._database.get_current_session().scalars(
            select(ProjectMemberTable).where(ProjectMemberTable.user_id == user_id)
        )
        return [ProjectMember.model_validate(row) for row in rows]

    async def count_by_role(self, project_id: UUID, role: ProjectRole) -> int:
        count = await self._database.get_current_session().scalar(
            select(func.count())
            .select_from(ProjectMemberTable)
            .where(ProjectMemberTable.project_id == project_id, ProjectMemberTable.role == role)
        )
        return count or 0

    async def save(self, project_member: ProjectMember) -> None:
        await self._database.get_current_session().merge(ProjectMemberTable(**project_member.model_dump()))

    async def delete(self, project_id: UUID, user_id: UUID) -> None:
        await self._database.get_current_session().execute(
            delete(ProjectMemberTable).where(
                ProjectMemberTable.project_id == project_id, ProjectMemberTable.user_id == user_id
            )
        )

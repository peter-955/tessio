from collections.abc import Mapping
from uuid import UUID

from sqlalchemy import select

from app.modules.gaps.ports.gap_assignee_directory import GapAssigneeDirectory
from app.modules.projects.infrastructure import ProjectMemberTable
from app.modules.users import UserStatus
from app.modules.users.infrastructure import UserTable
from app.shared.permissions import ProjectRole
from app.shared.postgres import Database


class PostgresGapAssigneeDirectory(GapAssigneeDirectory):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def list_active_member_ids(
        self, project_id: UUID, roles: frozenset[ProjectRole]
    ) -> Mapping[ProjectRole, list[UUID]]:
        member_ids: dict[ProjectRole, list[UUID]] = {role: [] for role in roles}
        if not roles:
            return member_ids
        result = await self._database.get_current_session().execute(
            select(ProjectMemberTable.role, ProjectMemberTable.user_id)
            .join(UserTable, UserTable.id == ProjectMemberTable.user_id)
            .where(
                ProjectMemberTable.project_id == project_id,
                ProjectMemberTable.role.in_(roles),
                UserTable.status == UserStatus.ACTIVE,
            )
            .order_by(ProjectMemberTable.user_id)
        )
        for role, user_id in result:
            member_ids[role].append(user_id)
        return member_ids

    async def find_active_member_role(self, project_id: UUID, user_id: UUID) -> ProjectRole | None:
        role: ProjectRole | None = await self._database.get_current_session().scalar(
            select(ProjectMemberTable.role)
            .join(UserTable, UserTable.id == ProjectMemberTable.user_id)
            .where(
                ProjectMemberTable.project_id == project_id,
                ProjectMemberTable.user_id == user_id,
                UserTable.status == UserStatus.ACTIVE,
            )
        )
        return role

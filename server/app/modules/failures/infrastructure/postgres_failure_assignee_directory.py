from uuid import UUID

from sqlalchemy import select

from app.modules.failures.ports.failure_assignee_directory import FailureAssigneeDirectory
from app.modules.projects.infrastructure import ProjectMemberTable
from app.modules.users import UserStatus
from app.modules.users.infrastructure import UserTable
from app.shared.postgres import Database


class PostgresFailureAssigneeDirectory(FailureAssigneeDirectory):
    def __init__(self, database: Database) -> None:
        self._database = database

    async def is_active_member(self, project_id: UUID, user_id: UUID) -> bool:
        member_id = await self._database.get_current_session().scalar(
            select(ProjectMemberTable.id)
            .join(UserTable, UserTable.id == ProjectMemberTable.user_id)
            .where(
                ProjectMemberTable.project_id == project_id,
                ProjectMemberTable.user_id == user_id,
                UserTable.status == UserStatus.ACTIVE,
            )
        )
        return member_id is not None
